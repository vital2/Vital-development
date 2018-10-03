from django.core.management.base import BaseCommand, CommandError
from django.contrib.sessions.models import Session
import logging
import time
from django.utils import timezone
from vital.models import VLAB_User, Course, User_VM_Config, Available_Config
from vital.views import stop_vms_during_logout
from vital.utils import XenClient, audit
from subprocess import Popen, PIPE
from random import randint
from django.core.mail import send_mail
import os
import signal

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = "Command to force remove VMs, networks of users who have not logged out properly " \
           "- Scheduled cron job that runs every 1 hour"

    def handle(self, *args, **options):
        while True:
            now = timezone.now()
            sessions = Session.objects.filter(expire_date__lt=now)
            for session in sessions:
                kill = True
                user_id = session.get_decoded().get('_auth_user_id')

                if user_id is not None:
                    logger.debug('session user_id:' +user_id)
                    user = VLAB_User.objects.get(id=user_id)
                    stupid_user = False
                    logger.debug("Checking session time for user : " + user.email)

                    started_vms = User_VM_Config.objects.filter(user_id=user_id)
                    for started_vm in started_vms:
                        logger.debug("Course : " + started_vm.vm.course.name)
                        logger.debug("Course auto shutdown period (mins): " + str(started_vm.vm.course.auto_shutdown_after))
                        logger.debug("VM: " + str(started_vm.vm.name))
                        time_difference_in_minutes = (now - session.expire_date).total_seconds() / 60
                        logger.debug("VM up after session expiry: " + str(time_difference_in_minutes))
                        if int(time_difference_in_minutes) >= started_vm.vm.course.auto_shutdown_after * 60:
                            try:
                                os.kill(int(started_vm.no_vnc_pid), signal.SIGTERM)
                            except OSError as e:
                                logger.error('Error stopping NoVNC Client with PID ' + str(started_vm.no_vnc_pid) + str(e))

                            XenClient().stop_vm(started_vm.xen_server, user, started_vm.vm.course.id, started_vm.vm.id)
                            config = Available_Config()
                            config.category = 'TERM_PORT'
                            config.value = started_vm.terminal_port
                            config.save()
                            if not started_vm.vm.course.allow_long_running_vms:
                                stupid_user = True
                            started_vm.delete()
                        else:
                            kill = False
                    if stupid_user:
                        send_mail("Vital : Illegal usage", 'Hi ' + user.first_name+', \r\n\r\nYou did not log off VMs the '
                                                                                'last time you used the Vital Platform. '
                                                                                'Please read the user manual [wiki] to '
                                                                                'understand how to use the platform. '
                                                                                'Not shutting down VMs will lead to the '
                                                                                'VMs to being corrupted. Please be '
                                                                                'careful.\r\n\r\nVital Admin',
                                'no-reply-vital@nyu.edu', [user.email], fail_silently=False)
                    #    Prof Tom was against penalizing students - hence commented. Good man :)
                    #    user.is_active = False
                    #    activation_code = randint(100000, 999999)
                    #    user.activation_code = activation_code
                    #    user.save()
                    #    blocked = Blocked_User()
                    #    blocked.user_id = user.id
                    #    blocked.save()
                if kill:
                    session.delete()

            time.sleep(3600) # Run every 1 hour
