from django.core.management.base import BaseCommand
from glob import glob
import logging
import ConfigParser
import os, errno, shutil
from vital.models import VLAB_User, Course, Registered_Course, User_Network_Configuration, Available_Config, \
    User_Bridge, Local_Network_MAC_Address

config = ConfigParser.ConfigParser()
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Rebases all VM's of stundets specified"

    def add_arguments(self, parser):
        parser.add_argument(
            '-c', '--course number',
            action='store',
            dest='course_id',
            help='course id',
            required=True
        )
        parser.add_argument(
            '-u', '--user id',
            action='store',
            dest='user_id',
            help='User Id',
            required=False
        )

    def handle(self, *args, **options):
        course_id = int(options['course_id'])
        user_id = int(options['user_id'])
        regUsers = []

        course = Course.objects.get(id=course_id)

        if user_id:
            user = VLAB_User.objects.get(id=user_id)
            regUsers.append(user)
        else:
            regUsers = Registered_Course.objects.filter(course=course)

        for user in regUsers:
            user = VLAB_User.objects.get(id=user.user_id)
            self.delete_student_configs(user, course)
            self.create_student_configs(user, course)
            print 'Reset Conf Files for user {} {} in Course {}'.format(user.first_name, user.last_name, course.name)

    def copyFile(self, src, dst, buffer_size=10485760, perserveFileDate=True):
        '''
        Copies a file to a new location. Overriding the Apache Commons due to use of larger 
        buffer much faster performance than before.
        @param src:    Source File
        @param dst:    Destination File (not file path)
        @param buffer_size:    Buffer size to use during copy
        @param perserveFileDate:    Preserve the original file date
        '''
        # Check to make sure destination directory exists. If it doesn't create the directory
        dstParent, dstFileName = os.path.split(dst)
        if(not(os.path.exists(dstParent))):
            os.makedirs(dstParent)

        # Optimize the buffer for small files
        buffer_size = min(buffer_size,os.path.getsize(src))
        if(buffer_size == 0):
            buffer_size = 1024

        if shutil._samefile(src, dst):
            raise shutil.Error("`%s` and `%s` are the same file" % (src, dst))
        for fn in [src, dst]:
            try:
                st = os.stat(fn)
            except OSError:
                # File most likely does not exist
                pass
            else:
                # XXX What about other special files? (sockets, devices...)
                if shutil.stat.S_ISFIFO(st.st_mode):
                    raise shutil.SpecialFileError("`%s` is a named pipe" % fn)

        with open(src, 'rb') as fsrc:
            with open(dst, 'wb') as fdst:
                shutil.copyfileobj(fsrc, fdst, buffer_size)

        if(perserveFileDate):
            shutil.copystat(src, dst)


    def delete_student_configs(self, user, course):
        logger.debug("Removing User Network configs...")
        for vm in course.virtual_machine_set.all():
            name = user.id + '_' + course.id + '_' + vm.id
            try:
                os.remove(config.get("VMConfig", "VM_CONF_LOCATION") + '/' + name + '.conf')
                logger.debug('Removed conf file for ' + name)
            except OSError as e:
                if e.errno != errno.ENOENT:
                    logger.error(' Error while removing VM conf - {}'.format(name))
                    logger.error(str(e).rstrip())
                    raise Exception('ERROR : cannot remove the vm - conf '
                                    '\n Reason : %s' % str(e).rstrip())

    def create_student_configs(self, user, course):
        logger.debug('Number of VMs in course: ' + str(len(course.virtual_machine_set.all())))
        for vm in course.virtual_machine_set.all():
            net_confs = User_Network_Configuration.objects.filter(user_id=user.id, vm=vm,
                                                                course=course).order_by('id')
            vif = ''
            for conf in net_confs:
                vif = vif + '\'mac=' + conf.mac_id + ', bridge=' + conf.bridge.name + '\','

            vif = vif[:len(vif) - 1]
            logger.debug('Registering with vif:' + vif + ' for user ' + user.email)

            name = user.id + '_' + course.id + '_' + vm.id
            base_vm = course.id + '_' + vm.id
            
            try:
            self.copyFile(config.get("VMConfig", "VM_CONF_LOCATION") + '/clean/' + base_vm + '.conf',
                     config.get("VMConfig", "VM_CONF_LOCATION") + '/' + name + '.conf', perserveFileDate=False)
            except Exception as e:
                logger.error(' Error while creating VM conf - {}'.format(name))
                logger.error(str(e).rstrip())
                raise Exception('ERROR : cannot setup the vm - conf '
                                '\n Reason : %s' % str(e).rstrip())

            f = open(config.get("VMConfig", "VM_CONF_LOCATION") + '/' + name + '.conf', 'r')
            file_data = f.read()
            f.close()

            new_data = file_data.replace('<VM_NAME>', name)
            if vif is not None:
                new_data = new_data + '\nvif=[' + vif + ']'

            f = open(config.get("VMConfig", "VM_CONF_LOCATION") + '/' + name + '.conf', 'w')
            f.write(new_data)
            f.close()
            logger.debug('Setup conf file for ' + name)
            logger.debug('Finished setting up ' + name)
            logger.debug('Registered user ' + user.email)

