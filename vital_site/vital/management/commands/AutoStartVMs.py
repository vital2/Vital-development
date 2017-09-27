from django.core.management.base import BaseCommand, CommandError
from vital.models import Auto_Start_Resources, VLAB_User
from vital.utils import XenServer
import time
import ConfigParser
import logging

logger = logging.getLogger(__name__)
config = ConfigParser.ConfigParser()
config.optionxform=str

# TODO change to common config file in shared location
config.read("/home/vital/config.ini")


# This is called by upstart job on reboot
class Command(BaseCommand):

    help = "Command to start VMs that are configured for course to auto start - " \
           "Scheduled by upstart job that runs on start up"

    def handle(self, *args, **options):
        logger.debug("Starting special VMs")
        server_configs = config.items('Servers')
        vms = Auto_Start_Resources.objects.filter(type='VM')
        user = VLAB_User.objects.get(first_name='Cron', last_name='User')
        for key, server_url in server_configs:
            for vm in vms:
                try:
                    XenServer(key, server_url).start_vm(user, vm.name.strip()+'_'+key.strip())
                except Exception as e:
                    logger.error("Could not autostart vm in "+key+" Reason:"+str(e))

