from django.contrib.sessions.models import Session
from django.conf import settings
import datetime
import logging
from utils import XenClient, SneakyXenLoadBalancer
from models import VLAB_User
import time


logger = logging.getLogger(__name__)  # check and add a handler for this.

# use this file to add all cron jobs - house keeping jobs etc

# do not forget to run
# python manage.py crontab add - to add jobs
# python manage.py crontab remove -  to remove jobs
# python manage.py crontab show - to view active jobs

def force_logout_inactive_users():
    print Session.objects.all()
    sessions = Session.objects.all().filter(expire_date__lte=datetime.datetime.now())
    print sessions
    for session in sessions:
        logger.debug(session.get_decoded().get('_auth_user_id'))
        print session.get_decoded().get('_auth_user_id')
        session.delete()
        # do machine shut down and other cleanup activities here


def clean_zombie_vms():
    # Might not even need this in future
    # TODO this needs to be fixed to check for all Xen machines
    user = VLAB_User.objects.get(email='rdj259@nyu.edu')
    vms = XenClient().list_all_vms('xen-server-dev-1', user)
    for vm in vms:
        if vm['name'].strip() == '(null)':
            XenClient().kill_zombie_vm('xen-server-dev-1', user, vm['id'])


def run_server_stats():
    # sneaks in server status every 10s to remove requirement of checking for every xen-api call
    logger.debug('Running server statistics <>')
    print "Start : %s" % time.ctime()
    SneakyXenLoadBalancer.sneak_in_server_stats()
    time.sleep(5)
    print "End : %s" % time.ctime()