from django.core.management.base import BaseCommand, CommandError
import logging
from django.core.mail import send_mail
from vital.models import VLAB_User

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = "Command to email common notifications to all relevant users"

    def add_arguments(self, parser):
        parser.add_argument(
            '-s', '--subject',
            action='store',
            dest='subject',
            help='specify email subject',
            required=True
        )
        parser.add_argument(
            '-b', '--body',
            action='store',
            dest='body',
            help='specify email body',
        )

    def handle(self, *args, **options):
        to_email = []
        subject = options['subject']
        body = options['body']
        for email in VLAB_User.objects.all():
            to_email.append(email)
        try:
            logger.debug('Generating notification mails for users')
            send_mail(subject, 'Hi, ' + body, 'no-reply-vital@nyu.edu', to_email, fail_silently=False)
        except Exception as e:
            logger.error(str(e))
