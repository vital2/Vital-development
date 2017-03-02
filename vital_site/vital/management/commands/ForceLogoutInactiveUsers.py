from django.core.management.base import BaseCommand, CommandError
from django.contrib.sessions.models import Session
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):
        sessions = Session.objects.filter(expire_date__lt=datetime.now())
        for session in sessions:
            user = session.get_decoded().get('_auth_user_id')
            if user is not None:
                logger.debug('session user_id:' +user)
            else:
                logger.debug('session user_id:Unknown')