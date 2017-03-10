from django.core.management.base import BaseCommand, CommandError
from vital.models import VLAB_User, Blocked_User
from django.core.mail import send_mail
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = "DEPRECATED : Command to unblock specified user"

    def add_arguments(self, parser):
        parser.add_argument('email', type=str)

    def handle(self, *args, **options):
        email = options['email']
        try:
            user = VLAB_User.objects.get(email=email)
            blocked = Blocked_User.objects.get(user_id=user.id)
            logger.debug('Generating re-activation mail for ' + user.email)
            send_mail('Activation mail', 'Hi ' + user.first_name + ',\r\n\n Welcome back to Vital. '
                                                                   'Please use activation code : ' +
                      str(user.activation_code) + ' for re-activating your account.\r\n\nVital',
                      'no-reply-vital@nyu.edu', [user.email], fail_silently=False)
            blocked.delete()
        except VLAB_User.DoesNotExist:
            logger.debug('Specified email id not registered')
        except Blocked_User.DoesNotExist:
            logger.debug('Specified user is not blocked')