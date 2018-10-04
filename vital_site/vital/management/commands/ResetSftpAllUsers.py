from django.core.management.base import BaseCommand, CommandError
import logging
from subprocess import Popen, PIPE
from vital.models import VLAB_User

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Reset SFTP Account of user.'

    def handle(self, *args, **options):
        users = VLAB_User.objects.all()
        for user in users:
            if user.first_name not in ['Cron', 'as11552']:
                logger.debug("Modifying SFTP account")
                cmd = 'sudo /home/vital/vital2.0/source/virtual_lab/vital_site/scripts/sftp_account.sh create '+ \
                      user.sftp_account+' '+ user.sftp_pass + ' > /home/vital/vital2.0/log/sftp.log'
                p = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
                out, err = p.communicate()
                if not p.returncode == 0:
                    raise Exception('ERROR : cannot register sftp account. \n Reason : %s' % err.rstrip())
                logger.debug("SFTP account created")
