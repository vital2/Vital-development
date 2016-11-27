import logging
import xmlrpclib
from models import Audit, Available_Config, User_Network_Configuration, Virtual_Machine
import ConfigParser

logger = logging.getLogger(__name__)
config = ConfigParser.ConfigParser()
config.read("/home/rdj259/config.ini")


def audit(request, obj, action):
    logger.debug('In audit')
    if request.user.id is not None:
        audit_record = Audit(done_by=request.user.id, category=type(obj).__name__, item_id=obj.id, action=action)
    else:
        audit_record = Audit(done_by=0, category=type(obj).__name__, item_id=obj.id, action=action)
        logger.error('An action is being performed without actual user id.')
    audit_record.save()


class XenClient:

    def __init__(self):
        pass

    def list_student_vms(self, server, user, course_id):
        vms = LoadBalancer().get_server(server).list_vms(user)
        prefix = str(user.id) + '_' + str(course_id)
        return [vm for vm in vms if vm['name'].startswith(prefix)]

    def list_vm(self, server,  user, course_id, vm_id):
        logger.debug('>>>>>>>>IN LIST VM>>>>>>')
        vm = LoadBalancer().get_server(server).list_vm(user, str(user.id) + '_' + str(course_id) + '_' + str(vm_id))
        vm['xen_server'] = server
        return vm

    def register_student_vms(self, user, course):
        xen = LoadBalancer().get_best_server()
        logger.debug(len(course.virtual_machine_set.all()))
        for vm in course.virtual_machine_set.all():
            flag = True
            cnt = 0
            # hack to handle concurrent requests
            while flag:
                available_config = Available_Config.objects.filter(category='MAC_ADDR').order_by('id').first()
                locked_conf = Available_Config.objects.select_for_update().filter(id=available_config.id)
                cnt += 1
                if locked_conf is not None and len(locked_conf) > 0:
                    val = locked_conf[0].value
                    locked_conf.delete()
                    # TODO change this to accept other private networks
                    # Done just to accept class nets
                    class_net = vm.network_configuration_set.filter(is_course_net=True).first()
                    vif = '\'mac=' + val + ', bridge=' + class_net.name + '\''
                    logger.debug('Registering with vif:'+vif+' for user '+user.email)
                    xen.setup_vm(user, str(user.id) + '_' + str(course.id) + '_' + str(vm.id),
                                 str(course.id) + '_' + str(vm.id), vif)
                    user_net_config = User_Network_Configuration()
                    user_net_config.bridge_name = class_net.name
                    user_net_config.user_id = user.id
                    user_net_config.mac_id = val
                    user_net_config.vm = vm
                    user_net_config.save()
                    logger.debug('Registered user ' + user.email)
                    flag = False
                if cnt >= 100:
                    raise Exception('Server Busy : Registration incomplete')




    def unregister_student_vms(self, server, user, course):
        xen = LoadBalancer().get_server(server)
        for virtualMachine in course.virtual_machine_set.all():
            # xen.stop_vm(user, str(user.id) + '_' + str(course.id) + '_' + str(vm.id))
            xen.cleanup_vm(user, str(user.id) + '_' + str(course.id) + '_' + str(virtualMachine.id))
            net_confs_to_delete = User_Network_Configuration.objects.filter(user_id=user.id, vm=virtualMachine)
            if len(net_confs_to_delete) > 0:
                for conf in net_confs_to_delete:
                    available_conf = Available_Config()
                    available_conf.category = 'MAC_ADDR'
                    available_conf.value = conf.mac_id
                    available_conf.save()
                    conf.delete()


    def start_vm(self, user, course_id, vm_id):
        logger.debug('XenClient - in start_vm')
        xen = LoadBalancer().get_best_server()
        vm = xen.start_vm(user, str(user.id) + '_' + str(course_id) + '_' + str(vm_id))
        vm['xen_server'] = xen.name
        return vm

    def stop_vm(self, server, user, course_id, vm_id):
        xen = LoadBalancer().get_server(server)
        xen.stop_vm(user, str(user.id) + '_' + str(course_id) + '_' + str(vm_id))

    def rebase_vm(self, user, course_id, vm_id):
        xen = LoadBalancer().get_best_server()
        virtual_machine = Virtual_Machine.objects.get(id=vm_id)
        net_confs = User_Network_Configuration.objects.filter(user_id=user.id, vm=virtual_machine)
        vif = ''
        for conf in net_confs:
            vif = vif + '\'mac=' + conf.mac_id + ', bridge=' + conf.bridge_name + '\','
        vif = vif[:len(vif)-1]
        xen.setup_vm(user, str(user.id) + '_' + str(course_id) + '_' + str(vm_id), str(course_id) + '_' + str(vm_id),
                     vif)

    def save_vm(self, server, user, course_id, vm_id):
        xen = LoadBalancer().get_server(server)
        xen.save_vm(user, str(user.id) + '_' + str(course_id) + '_' + str(vm_id))

    def restore_vm(self, server, user, course_id, vm_id):
        xen = LoadBalancer().get_server(server)
        xen.restore_vm(user, str(user.id) + '_' + str(course_id) + '_' + str(vm_id), str(course_id) + '_' + str(vm_id))


class XenServer:

    def __init__(self, name, url):
        self.name = name
        self.proxy = xmlrpclib.ServerProxy(url)

    def list_vms(self, user):
        return self.proxy.xenapi.list_all_vms(user.email, user.password)

    def list_vm(self, user, vm_name):
        return self.proxy.xenapi.list_vm(user.email, user.password, vm_name)

    def setup_vm(self, user, vm_name, base_name, vif=None):
        self.proxy.xenapi.setup_vm(user.email, user.password, vm_name, base_name, vif)

    def cleanup_vm(self, user, vm_name):
        self.proxy.xenapi.cleanup_vm(user.email, user.password, vm_name)

    def stop_vm(self, user, vm_name):
        self.proxy.xenapi.stop_vm(user.email, user.password, vm_name)

    def start_vm(self, user, vm_name):
        return self.proxy.xenapi.start_vm(user.email, user.password, vm_name)

    def save_vm(self, user, vm_name):
        return self.proxy.xenapi.save_vm(user.email, user.password, vm_name)

    def restore_vm(self, user, vm_name, base_vm):
        return self.proxy.xenapi.restore_vm(user.email, user.password, vm_name, base_vm)


class LoadBalancer:

    def get_best_server(self):
        # server_configs = config.items('Servers')
        #  TODO find best server
        # servers = []
        # for key, server_url in server_configs:
        #    servers.append(XenServer(key, server_url))
        return XenServer('xen-server-dev-1', 'http://192.168.35.33:8000')

    def get_server(self, name):
        return XenServer(name, config.get("Servers", name))
