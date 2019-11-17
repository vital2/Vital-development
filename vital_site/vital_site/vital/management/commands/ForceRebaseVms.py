from django.core.management.base import BaseCommand
import logging
from vital.models import VLAB_User, Course, Registered_Course 
from vital.utils import XenClient

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
            '-vm', '--vm number',
            action='store',
            dest='vm_id',
            help='vmid',
            required=True
        )

    def handle(self, *args, **options):
        course_id = int(options['course_id'])
        vm_id = int(options['vm_id'])

        course = Course.objects.get(id=course_id)

        regUsers = Registered_Course.objects.filter(course=course)
        for user in regUsers:
            user = VLAB_User.objects.get(id=user.user_id)
            print user.first_name
            XenClient().rebase_vm(user, course_id, vm_id)
            print 'Re-imaged Virtual machine for student {} {} in Course {}'.format(user.first_name, user.last_name, course.name)

