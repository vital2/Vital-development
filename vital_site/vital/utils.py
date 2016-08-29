import logging
import xmlrpclib
from models import Audit
logger = logging.getLogger(__name__)


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

    def list_student_vms(self, user, course_id):
        vms = XenServer('http://128.238.77.10:8000').list_vms(user)
        prefix = str(user.id) + '_' + str(course_id)
        logger.debug(prefix)
        logger.debug(vms)
        return [vm for vm in vms if vm['name'].startswith(prefix)]

    def list_vm(self, user, vm_name):
        XenServer('http://128.238.77.10:8000').list_vm(vm_name)

    def register_student_vms(self, user, course):
        xen = XenServer('http://128.238.77.10:8000')
        for vm in course.virtual_machine_set.all():
            xen.register_vm(user, str(user.id)+'_'+str(course.id)+'_'+str(vm.id), str(course.id)+'_'+str(vm.id))

    def unregister_student_vms(self, user, course):
        xen = XenServer('http://128.238.77.10:8000')
        for vm in course.virtual_machine_set.all():
            xen.stop_vm(user, str(user.id) + '_' + str(course.id) + '_' + str(vm.id))
            xen.unregister_vm(user, str(user.id) + '_' + str(course.id) + '_' + str(vm.id))


class XenServer:

    def __init__(self, url):
        self.proxy = xmlrpclib.ServerProxy(url)

    def list_vms(self, user):
        vms = self.proxy.xenapi.list_all_vms(user.email, user.password)
        logger.debug(len(vms))
        return vms

    def list_vm(self, user, vm_name):
        vm = self.proxy.xenapi.list_vm(user.email, user.password, vm_name)
        return vm

    def register_vm(self, user, vm_name, base_name):
        self.proxy.xenapi.register_vm(user.email, user.password, vm_name, base_name)

    def unregister_vm(self, user, vm_name):
        self.proxy.xenapi.unregister_vm(user.email, user.password, vm_name)

    def stop_vm(self, user, vm_name):
        self.proxy.xenapi.stop_vm(user.email, user.password, vm_name)