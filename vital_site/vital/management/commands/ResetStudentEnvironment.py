from django.core.management.base import BaseCommand, CommandError
from vital.models import Available_Config, Registered_Course, VLAB_User, User_VM_Config
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = "Command to cleanup user VMs and networks for a particular course from Xen and database"

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
        course = options['course']
        resetmode = options['resetmode']

        try:
            user = VLAB_User.objects.get(email=email)
            registered_course = Registered_Course.objects.get(user_id=user.id, course__id=course)
            logger.debug(registered_course.course.name)
            for vm in registered_course.course.virtual_machine_set.all():
                try:
                    user_vms = vm.user_vm_config_set.get(user_id=user.id)
                    logger.debug(len(user_vms))
                except User_VM_Config.DoesNotExist:
                    logger.debug('Not started')

        except VLAB_User.DoesNotExist:
            logger.error('User with specified email not found!')
        except Registered_Course.DoesNotExist:
            logger.error('User is not registered for specified course!')
