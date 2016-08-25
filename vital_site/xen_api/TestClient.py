import xmlrpclib
from pprint import pprint

proxy = xmlrpclib.ServerProxy('http://128.238.77.10:8000')

# listing all vms
print "Listing all VMs..."
pprint(proxy.xenapi.list_all_vms('richiedjohnson@yahoo.co.in', 'Test123!'))

# listing specific vm
print "Listing specific VM..."
pprint(proxy.xenapi.list_vm('bt5-qemu14'))

print "Stopping vm if exists..."
proxy.xenapi.stop_vm('bt5-qemu73')

print "Starting VM..."
vm = proxy.xenapi.start_vm('bt5-qemu73')
pprint(vars(vm))

print "Stopping created VM..."
proxy.xenapi.stop_vm('bt5-qemu73')
