from django.core.management.base import BaseCommand, CommandError
from django.contrib.sessions.models import Session
import logging
from django.utils import timezone
from vital.models import VLAB_User, Course, User_VM_Config, Available_Config
from vital.views import stop_vms_during_logout
from vital.utils import XenClient, audit
from subprocess import Popen, PIPE
from random import randint
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = "Command to force remove VMs, networks of users who have not logged out properly " \
           "- Scheduled cron job that runs every 1 hour"

    def handle(self, *args, **options):
        now = timezone.now()
        sessions = Session.objects.filter(expire_date__lt=now)
        for session in sessions:
            kill = True
            user_id = session.get_decoded().get('_auth_user_id')

            if user_id is not None:
                logger.debug('session user_id:' +user_id)
                user = VLAB_User.objects.get(id=user_id)
                stupid_user = False
                logger.debug("Force shutting down VMs for user : " + user.email)

                started_vms = User_VM_Config.objects.filter(user_id=user_id)
                for started_vm in started_vms:
                    logger.debug("Course : " + started_vm.vm.course.name)
                    logger.debug("Course auto shutdown period (mins): " + str(started_vm.vm.course.auto_shutdown_after))
                    logger.debug("VM: " + str(started_vm.vm.name))
                    time_difference_in_minutes = (now - session.expire_date).total_seconds() / 60
                    logger.debug("VM up after session expiry: " + str(time_difference_in_minutes))
                    if int(time_difference_in_minutes) >= started_vm.vm.course.auto_shutdown_after:
                        cmd = 'kill ' + started_vm.no_vnc_pid
                        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
                        out, err = p.communicate()
                        if not p.returncode == 0:
                            if 'No such process' not in err.rstrip():
                                raise Exception('ERROR : cannot stop the vm '
                                                '\n Reason : %s' % err.rstrip())
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
                    send_mail("Vital : Illegal usage", 'Hi ' + user.first_name+', \r\n\r\n You did not log off VMs the '
                                                                               'last time you used the vital platform. '
                                                                               'Please read the user manual [wiki] to '
                                                                               'understand how to use the platform. '
                                                                               'Not shutting down VMs will lead to the '
                                                                               'VMs to being corrupted and user being '
                                                                               'blocked/ \r\n\r\nVital Admin team',
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
