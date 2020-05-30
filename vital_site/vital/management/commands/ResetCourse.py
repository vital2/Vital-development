from django.core.management.base import BaseCommand, CommandError
import logging
from django.utils import timezone
from vital.models import Course, VLAB_User, Registered_Course, User_Bridge, User_Session, User_Network_Configuration, Available_Config, User_VM_Config
from django.utils.crypto import get_random_string
import ConfigParser
import os
import errno

logger = logging.getLogger(__name__)
config = ConfigParser.ConfigParser()
config.optionxform=str

# TODO change to common config file in shared location
config.read("/home/vital/config.ini")

class Command(BaseCommand):
    help = "resets a course to remove all students and generate a new registration code"

    def add_arguments(self, parser):
        parser.add_argument(
            '-c', '--course',
            action='store',
            dest='course_id',
            help='specify course id',
            required=True
        )

    def delete_student_configs(self, user_id, course):
        logger.debug("Removing User configs...")
        conf_path = config.get("VMConfig", "VM_CONF_LOCATION")
        qcow_path = "/mnt/vlab-datastore/vital/vm_dsk"
        for vm in course.virtual_machine_set.all():
            name = '{}_{}_{}'.format(user_id, course.id, vm.id)
            try:
                os.remove(conf_path + '/' + name + '.conf')
                os.remove(qcow_path + '/' + name + '.qcow')
                logger.debug('Removed files for ' + name)
            except OSError as e:
                if e.errno != errno.ENOENT:
                    logger.error(' Error while removing file - {}'.format(name))
                    logger.error(str(e).rstrip())
                    raise Exception('ERROR : cannot remove the vm - conf '
                                    '\n Reason : %s' % str(e).rstrip())
     
    def handle(self, *args, **options):
        course_id = options['course_id']
        course = Course.objects.get(id=course_id)
        print "Removing students for course: "+course.name+" (ID:"+ str(course.id) +")"
        for user_id in (Registered_Course.objects.filter(course=course)).values_list("user_id", flat=True):
            self.delete_student_configs(user_id, course)
            print "Removing User Sessions for Course"
            try:
                session = User_Session.objects.filter(user_id=user_id)
                session.delete()
            except:
                logger.error('Error while removing user session for user' + user_id)
                raise Exception('ERROR: Cannot remove User sessions')
        print "Removing student from vital user table"
        for user_id in (Registered_Course.objects.filter(course=course)).values_list("user_id", flat=True):
            try:
                user = VLAB_User.objects.filter(id=user_id)
                user.delete()
            except:
                logger.error('Error while removing user from vital user table for user' + user_id)
        print "Removing registered students"
        Registered_Course.objects.filter(course=course).delete()
        print "Removing registered user network configs"
        user_nets = User_Network_Configuration.objects.filter(course=course)
        for net in user_nets:
            conf = Available_Config()
            conf.category = 'MAC_ADDR'
            conf.value = net.mac_id
            try:
                bridge = net.bridge
                bridgeval = User_Bridge.objects.filter(name=bridge.name)
                #bridgeval.delete() #delete the bridge entry in the table
            except:
                logger.error('Error while removing user bridges')

            bridgeval.delete()
            conf.save()
            net.delete()
        print "Removed User Bridges"
        print "Setting new registration code"
        reg_code = get_random_string(length=8)
        course.registration_code = reg_code
        course.save()
        print "The course has been reset. The new registration code is " + reg_code
