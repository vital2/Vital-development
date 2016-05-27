from django.contrib.sessions.models import Session
from django.conf import settings
import datetime
import logging

logger = logging.getLogger(__name__)  # check and add a handler for this.

def force_logout_inactive_users():
    print Session.objects.all()
    sessions = Session.objects.all().filter(expire_date__lte=datetime.datetime.now())
    print sessions
    for session in sessions:
        logger.debug(session.get_decoded().get('_auth_user_id'))
        print session.get_decoded().get('_auth_user_id')
        session.delete()
        # do machine shut down and other cleanup activities here

# use this file to add all cron jobs - house keeping jobs etc

# do not forget to run
# python manage.py crontab add - to add jobs
# python manage.py crontab remove -  to remove jobs
# python manage.py crontab show - to view active jobs
