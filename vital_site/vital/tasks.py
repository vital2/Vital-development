import configparser
import logging
import os
import zmq
import redis

<<<<<<< HEAD
from utils import XenClient
from models import VLAB_User, User_VM_Config

logger = logging.getLogger(__name__)
config_ini = ConfigParser.ConfigParser()
=======
from vital.utils import XenClient
from vital.models import VLAB_User, User_VM_Config

logger = logging.getLogger(__name__)
config_ini = configparser.ConfigParser()
>>>>>>> 7f2f8b96592d27ff0fed41e387b55cef37452a96
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
        vm = User_VM_Config.objects.get(user_id=user_id, vm_id=vm_id)

        # Remove Network Bridges
        user = VLAB_User.objects.get(id = user_id)
        XenClient().remove_network_bridges(vm.xen_server, user, course_id, vm_id)

        vm.delete()

        # Delete Redis Token
        r = redis.Redis(host=redis_host, port=redis_port, password=redis_password, db=0)
        logger.debug('Removing Token : {}'.format(vm.token))
        r.delete(vm.token)

    except Exception as e:
        logger.error(str(e))
