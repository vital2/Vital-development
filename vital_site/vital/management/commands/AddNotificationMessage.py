from django.core.management.base import BaseCommand, CommandError
from vital.models import Available_Config
import logging


logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = "Command to add notification message to vital web pages for all users"

    def add_arguments(self, parser):
        parser.add_argument(
            '-m', '--message',
            action='store',
            dest='message',
            help='specify message to be displayed on all page',
        )

    def handle(self, *args, **options):
        if options['message'] is not None or options['message'].strip() != '':
            config = None
            try:
                config = Available_Config.objects.get(category='NOTIFICATION_MESSAGE')
            except Available_Config.DoesNotExist as e:
                config = Available_Config()
                config.category = 'NOTIFICATION_MESSAGE'
            config.value = options['message']
            config.save()
            logger.debug('Notification Message set as -' + config.value)
        else:
            logger.info('ERROR : Message cannot be empty!!')
