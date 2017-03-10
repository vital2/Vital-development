from django.core.management.base import BaseCommand, CommandError
from vital.utils import SneakyXenLoadBalancer
import time
import logging

logger = logging.getLogger(__name__)


# This is called by upstart job on reboot
class Command(BaseCommand):

    help = "Command that starts xen stats collection - scheduled to start on server boot"

    def handle(self, *args, **options):
        logger.debug("Starting the stats collector")
        while True:
            SneakyXenLoadBalancer().sneak_in_server_stats()
            time.sleep(5)  # 5 second heart beat
