from django.core.management.base import BaseCommand, CommandError
from vital.models import Available_Config
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
        )
        parser.add_argument(
            '-r', '--resetmode',
            action='store',
            dest='resetmode',
            default='soft',
            help='specify reset mode - (hard/soft)',
        )

    def handle(self, *args, **options):
        user = options['user']
        course = options['course']
        resetmode = options['resetmode']

        if user is None or user.strip() != '':
