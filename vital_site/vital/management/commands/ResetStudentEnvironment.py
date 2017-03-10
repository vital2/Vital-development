from django.core.management.base import BaseCommand, CommandError
from vital.models import Available_Config
import logging
from optparse import make_option

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = "Command to cleanup user VMs and networks for a particular course from Xen and database"

    option_list = BaseCommand.option_list + (
        make_option(
            "-u",
            dest="user",
            help="specify user email",
            metavar="USER"
        ),
        make_option(
            "-c",
            dest="course",
            help="specify course id",
            metavar="COURSE"
        ),
        make_option(
            "-reset",
            dest="reset",
            help="specify soft/hard reset",
            metavar="COURSE"
        ),
    )

    def handle(self, *args, **options):
        logger.debug('user : '+ options['user'])
        logger.debug('course:'+ options['course'])
        logger.debug('course:' + options['course'])