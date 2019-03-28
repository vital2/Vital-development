import ConfigParser
import logging
import os
# import signal
import zmq
import redis
# from subprocess import Popen, PIPE

# from django.db import transaction

from utils import XenClient
from models import VLAB_User, User_VM_Config

logger = logging.getLogger(__name__)
config_ini = ConfigParser.ConfigParser()
config_ini.optionxform=str

# TODO change to common config file in shared location
config_ini.read("/home/vital/config.ini")

def release_vm(user_id, course_id, vm_id):
    logger.debug("in releaseVM")
    error_message = ''

    redis_host = config_ini.get('VITAL', 'REDIS_HOST')
    redis_port = int(config_ini.get('VITAL', 'REDIS_PORT'))
    redis_password = config_ini.get('VITAL', 'REDIS_PASS')

    try:
        # Get the VM Details in request
        # with transaction.atomic():
        vm = User_VM_Config.objects.get(user_id=user_id, vm_id=vm_id)

        # Delete Redis Token
        r = redis.Redis(host=redis_host, port=redis_port, password=redis_password, db=0)
        logger.debug('Removing Token : {}'.format(vm.token))
        r.delete(vm.token)

        # logger.debug('VM VNC Process ID : {}'.format(vm.no_vnc_pid))

        # Remove Network Bridges
        user = VLAB_User.objects.get(id = user_id)
        XenClient().remove_network_bridges(vm.xen_server, user, course_id, vm_id)

        # try:
        #     os.kill(int(vm.no_vnc_pid), signal.SIGTERM)
        # except OSError as e:
        #     logger.error('Error stopping NoVNC Client with PID ' + str(vm.no_vnc_pid) + str(e))

        vm.delete()

    except Exception as e:
        logger.error(str(e))
