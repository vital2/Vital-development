from django.core.management.base import BaseCommand, CommandError
from vital.models import Available_Config
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = "Command to remove notification message for all users from vital website"

    def handle(self, *args, **options):
        try:
            config = Available_Config.objects.get(category='NOTIFICATION_MESSAGE')
            config.delete()
        except Available_Config.DoesNotExist as e:
            pass
        logger.debug('Notification Message removed!')
