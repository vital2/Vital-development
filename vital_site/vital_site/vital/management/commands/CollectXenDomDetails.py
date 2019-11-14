from django.core.management.base import BaseCommand, CommandError
from vital.utils import SneakyXenLoadBalancer
import time
import logging

logger = logging.getLogger(__name__)


# This is called by upstart job on reboot
class Command(BaseCommand):

    help = "Command to collect Xen DOM Details every minute - scheduled to start on server boot"

    def handle(self, *args, **options):
        logger.debug("Collecting Xen DOM Details on each Server")
        while True:
            SneakyXenLoadBalancer().get_xen_dom_details()
            time.sleep(60)  # 1 Minute heart beat
