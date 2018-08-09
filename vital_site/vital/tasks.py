import ConfigParser
import logging
import zmq
from subprocess import Popen, PIPE

from utils import XenClient
from models import VLAB_User, User_VM_Config, Available_Config

logger = logging.getLogger(__name__)

def release_vm(user_id, course_id, vm_id):
    logger.debug("in releaseVM")
    error_message = ''

    try:
        # Get the VM Details in request
        vm = User_VM_Config.objects.get(user_id=user_id, vm_id=vm_id)
        logger.debug('VM @ Display Port : {}'.format(vm.no_vnc_pid))

        # Remove Network Bridges
        user = VLAB_User.objects.get(id = user_id)
        XenClient().remove_network_bridges(vm.xen_server, user, course_id, vm_id)

        cmd = 'kill -9 ' + vm.no_vnc_pid
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        if not p.returncode == 0:
            if 'No such process' not in err.rstrip():
                logger.error('Error stopping NoVNC Client with PID ' + str(vm.no_vnc_pid) + '(' + err.rstrip() + ')')

        config = Available_Config()
        config.category = 'TERM_PORT'
        config.value = vm.terminal_port
        config.save()
        vm.delete()

    except Exception as e:
        logger.error(str(e))
