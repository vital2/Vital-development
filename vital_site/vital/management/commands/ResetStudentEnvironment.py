from django.core.management.base import BaseCommand, CommandError
from vital.models import Available_Config, Registered_Course, VLAB_User, User_VM_Config, User_Bridge, User_Session, Course
from vital.utils import XenServer, XenClient
import logging
from subprocess import Popen, PIPE
from django.contrib.sessions.models import Session
import ConfigParser
from django.db import transaction

logger = logging.getLogger(__name__)
config = ConfigParser.ConfigParser()
config.optionxform=str

# TODO change to common config file in shared location
config.read("/home/rdj259/config.ini")


class Command(BaseCommand):

    help = "Command to cleanup user VMs and networks for a particular course from Xen and database"

    def __init__(self):
        self.registered_courses = None
        self.user = None
        self.course = None

    def add_arguments(self, parser):
        parser.add_argument(
            '-u', '--user',
            action='store',
            dest='user',
            help='specify user email',
            required=True
        )
        parser.add_argument(
            '-c', '--course',
            action='store',
            dest='course',
            help='specify course id of user',
            required=True
        )
        parser.add_argument(
            '-r', '--resetmode',
            action='store',
            dest='resetmode',
            default='soft',
            help='specify reset mode - (hard/soft)',
        )

    def handle(self, *args, **options):
        email = options['user']
        course_id = options['course']
        resetmode = options['resetmode']

        try:
            self.user = VLAB_User.objects.get(email=email)
            self.course = Course.objects.get(id=course_id)
            self.registered_courses = Registered_Course.objects.get(user_id=self.user.id, course__id=course_id)

            logger.debug('Checking VMs..')
            for vm in self.registered_courses.course.virtual_machine_set.all():
                self.scan_and_kill_vm_on_xen(str(self.user.id)+'_'+str(course_id)+'_'+str(vm.id))

            logger.debug('Checking networks..')
            for network in self.registered_courses.course.network_configuration_set.filter(is_course_net=False).distinct('name'):
                self.scan_and_kill_bridges(str(self.user.id)+'_'+str(course_id)+'_'+network.name)

            logger.debug('Resetting bridges..')
            self.reset_bridge_state(course_id)

            logger.debug('Killing VNC and collecting resources back to pool..')
            self.kill_vnc(self.user)

            if resetmode == 'hard':
                with transaction.atomic():
                    logger.debug('Removing VM conf and VM dsks..')
                    XenClient().unregister_student_vms(self.user, self.course)
                    logger.debug('Recreating VM conf and VM dsks..')
                    XenClient().register_student_vms(self.user, self.course)

            logger.debug('Killing user session..')
            try:
                user_session = User_Session.objects.get(user_id=self.user.id)
                Session.objects.get(session_key=user_session.session_key).delete()
                user_session.delete()
            except User_Session.DoesNotExist:
                pass
            except Session.DoesNotExist:
                pass

        except VLAB_User.DoesNotExist:
            logger.error('User with specified email not found!')
        except Registered_Course.DoesNotExist:
            logger.error('User is not registered for specified course!')
        except Registered_Course.DoesNotExist:
            logger.error('Course not recognized!')
        except User_Session.DoesNotExist:
            pass

    def scan_and_kill_vm_on_xen(self, vm_name):
        server_configs = config.items('Servers')
        for key, server_url in server_configs:
            xen = XenServer(key, server_url)
            logger.debug('Scanning '+key+' for vm '+vm_name)
            if xen.vm_exists(self.user, vm_name):
                logger.debug('FOUND VM ' + vm_name + ' on ' + key + '..Stopping!!')
                xen.stop_vm(self.user, vm_name)

    def scan_and_kill_bridges(self, bridge_name):
        server_configs = config.items('Servers')
        for key, server_url in server_configs:
            xen = XenServer(key, server_url)
            logger.debug('Scanning ' + key + ' for bridge ' + bridge_name)
            if xen.bridge_exists(self.user, bridge_name):
                logger.debug('FOUND Bridge ' + bridge_name + ' on ' + key + '..Stopping!!')
                xen.remove_bridge(self.user, bridge_name)

    def reset_bridge_state(self, course_id):
        User_Bridge.objects.filter(name__startswith=str(self.user.id)+'_'+str(course_id)).update(created=False)

    def kill_vnc(self, user):
        for vm in self.registered_courses.course.virtual_machine_set.all():
            try:
                user_vm = vm.user_vm_config_set.get(user_id=user.id)
                logger.debug('Killing VNC for ' + vm.name)
                cmd = 'kill ' + user_vm.no_vnc_pid
                p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
                out, err = p.communicate()
                if not p.returncode == 0:
                    if 'No such process' not in err.rstrip():
                        raise Exception('ERROR : cannot stop the vm '
                                        '\n Reason : %s' % err.rstrip())
                available_conf = Available_Config()
                available_conf.category = 'TERM_PORT'
                available_conf.value = user_vm.terminal_port
                available_conf.save()
                user_vm.delete()
            except User_VM_Config.DoesNotExist:
                pass
