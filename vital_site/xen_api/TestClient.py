import xmlrpclib
from pprint import pprint

proxy = xmlrpclib.ServerProxy('http://128.238.77.10:8000')

print "Listing all VMs..."
print proxy.xenapi.list_all_vms('richiedjohnson@yahoo.co.in', 'Test123!')

print "Listing specific VM..."
pprint(proxy.xenapi.list_vm('richiedjohnson@yahoo.co.in', 'Test123!','bt5-qemu14'))

print "Registering new VM..."
proxy.xenapi.register_vm('richiedjohnson@yahoo.co.in', 'Test123!', 'GY12345_bt5', '3', '1')

print "Stopping vm if exists..."
proxy.xenapi.stop_vm('richiedjohnson@yahoo.co.in', 'Test123!', 'GY12345_bt5', '3', '1')

print "Starting VM..."
vm = proxy.xenapi.start_vm('richiedjohnson@yahoo.co.in', 'Test123!', 'GY12345_bt5', '3', '1')
pprint(vm)

print "Listing all VMs..."
print proxy.xenapi.list_all_vms('richiedjohnson@yahoo.co.in', 'Test123!')

print "Stopping created VM..."
proxy.xenapi.stop_vm('richiedjohnson@yahoo.co.in', 'Test123!', 'GY12345_bt5', '3', '1')

print "Unregistering VM"
proxy.xenapi.unregister_vm('richiedjohnson@yahoo.co.in', 'Test123!', 'GY12345_bt5', '3', '1')

print "Listing all VMs..."
print proxy.xenapi.list_all_vms('richiedjohnson@yahoo.co.in', 'Test123!')
