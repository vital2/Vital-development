from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
import logging
from . import views
from django.contrib.sessions.models import Session
from vital.models import User_Session


@receiver(user_logged_in)
def sig_user_logged_in(sender, user, request, **kwargs):
    logger = logging.getLogger(__name__)
    logger.info("user logged in: %s at %s" % (user, request.META['REMOTE_ADDR']))
    # Below is to keep track of sessions and remove old session keys
    try:
        user_session = User_Session.objects.get(user_id=user.id)
        Session.objects.filter(session_key=user_session.session_key).delete()
        user_session.delete()
    except User_Session.DoesNotExist:
        pass
    new_user_session = User_Session()
    new_user_session.user_id = user.id
    new_user_session.session_key = request.session.session_key
    new_user_session.save()


@receiver(user_logged_out)
def sig_user_logged_out(sender, user, request, **kwargs):
    logger = logging.getLogger(__name__)
    all_vms_shutdown = views.stop_vms_during_logout(user)
    if all_vms_shutdown:
        session = Session.objects.get(session_key=request.session.session_key)
        logger.debug('session key:' + session.session_key)
        user_id = session.get_decoded().get('_auth_user_id')
        User_Session.objects.filter(user_id=user_id).delete()
        session.delete()
    logger.info("user logged out: %s at %s" % (user, request.META['REMOTE_ADDR']))

    # do machine shut down and other cleanup activities here
