from django.core.management.base import BaseCommand, CommandError
from django.contrib.sessions.models import Session
import logging
from datetime import datetime
from vital.models import VLAB_User
from vital.views import stop_vms_during_logout

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):
        sessions = Session.objects.filter(expire_date__lt=datetime.now())
        for session in sessions:
            user_id = session.get_decoded().get('_auth_user_id')
            if user_id is not None:
                logger.debug('session user_id:' +user_id)
                user = VLAB_User.objects.get(id=user_id)
                logger.debug("Force shutting down VMs for user : "+user.email)
                stop_vms_during_logout(user)
            session.delete()
