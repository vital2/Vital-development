import ConfigParser
import logging
import os
import signal
import zmq
from subprocess import Popen, PIPE

from django.db import transaction

from utils import XenClient
from models import VLAB_User, User_VM_Config, Available_Config

logger = logging.getLogger(__name__)

def release_vm(user_id, course_id, vm_id):
    logger.debug("in releaseVM")
    error_message = ''

    try:
        # Get the VM Details in request
        with transaction.atomic():
            vm = User_VM_Config.objects.select_for_update().get(user_id=user_id, vm_id=vm_id)
            logger.debug('VM VNC Process ID : {}'.format(vm.no_vnc_pid))

            # Remove Network Bridges
            user = VLAB_User.objects.get(id = user_id)
            XenClient().remove_network_bridges(vm.xen_server, user, course_id, vm_id)

            try:
                os.kill(int(vm.no_vnc_pid), signal.SIGTERM)
            except OSError as e:
                logger.error('Error stopping NoVNC Client with PID ' + str(vm.no_vnc_pid) + str(e))

            vm.delete()

    except Exception as e:
        logger.error(str(e))
