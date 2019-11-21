from django.core.management.base import BaseCommand, CommandError
import logging
from django.core.mail import send_mail
from vital.models import VLAB_User
from random import randint

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "reset activation code for a user"

    def add_arguments(self, parser):
        parser.add_argument(
            '-e', '--email',
            action='store',
            dest='email',
            help='specify user email',
            required=True
        )

    def handle(self, *args, **options):
        email = options['email']
        user = VLAB_User.objects.get(email=email)
        user.is_active = False
        activation_code = randint(100000, 999999)
        user.activation_code = activation_code
        user.save()
        send_mail('Activation code reset mail',
                  'Hi ' + user.first_name + ',\r\n\n Please enter the activation code' + str(activation_code) +
                                            ' to access your vital account.' +
                  '.\r\n\nVital', 'no-reply-vital@nyu.edu', [user.email], fail_silently=False)
