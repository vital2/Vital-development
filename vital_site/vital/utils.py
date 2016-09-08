import logging
import xmlrpclib
from models import Audit
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
        logger.debug(prefix)
        logger.debug(vms)
        return [vm for vm in vms if vm['name'].startswith(prefix)]

    def list_vm(self, server,  user, vm_name):
        return LoadBalancer().get_server(server).list_vm(vm_name)

    def register_student_vms(self, user, course):
        xen = LoadBalancer().get_best_server()
        logger.debug(course.virtual_machine_set.all())
        for vm in course.virtual_machine_set.all():
            xen.setup_vm(user, str(user.id)+'_'+str(course.id)+'_'+str(vm.id), str(course.id)+'_'+str(vm.id))

    def unregister_student_vms(self, server, user, course):
        xen = LoadBalancer().get_server(server)
        for vm in course.virtual_machine_set.all():
            xen.stop_vm(user, str(user.id) + '_' + str(course.id) + '_' + str(vm.id))
            xen.cleanup_vm(user, str(user.id) + '_' + str(course.id) + '_' + str(vm.id))

    def start_vm(self, user, course_id, vm_id):
        xen = LoadBalancer().get_best_server()
        vm = xen.start_vm(user, str(user.id) + '_' + str(course_id) + '_' + str(vm_id))
        vm['xen_server'] = xen.name
        return vm

    def stop_vm(self, server, user, course_id, vm_id):
        xen = LoadBalancer().get_server(server)
        xen.stop_vm(user, str(user.id) + '_' + str(course_id) + '_' + str(vm_id))

    def rebase_vm(self, server, user, course, vm_id):
        xen = LoadBalancer().get_server(server)
        xen.stop_vm(user, str(user.id) + '_' + str(course.id) + '_' + str(vm_id))
        xen.setup_vm(user, str(user.id) + '_' + str(course.id) + '_' + str(vm_id), str(course.id) + '_' + str(vm_id))


class XenServer:

    def __init__(self, name, url):
        self.name = name
        self.proxy = xmlrpclib.ServerProxy(url)

    def list_vms(self, user):
        vms = self.proxy.xenapi.list_all_vms(user.email, user.password)
        logger.debug(len(vms))
        return vms

    def list_vm(self, user, vm_name):
        vm = self.proxy.xenapi.list_vm(user.email, user.password, vm_name)
        return vm

    def setup_vm(self, user, vm_name, base_name):
        self.proxy.xenapi.setup_vm(user.email, user.password, vm_name, base_name)

    def cleanup_vm(self, user, vm_name):
        self.proxy.xenapi.cleanup_vm(user.email, user.password, vm_name)

    def stop_vm(self, user, vm_name):
        self.proxy.xenapi.stop_vm(user.email, user.password, vm_name)

    def start_vm(self, user, vm_name):
        return self.proxy.xenapi.start_vm(user.email, user.password, vm_name)


class LoadBalancer:

    def get_best_server(self):
        server_configs = config.items('Servers')
        #  TODO find best server
        # servers = []
        # for key, server_url in server_configs:
        #    servers.append(XenServer(key, server_url))
        return XenServer('xen-server-dev-1', 'http://128.238.77.10:8000')

    def get_server(self, name):
        return XenServer(name, config.get("Servers", name))
