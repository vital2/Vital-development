import xmlrpclib
from pprint import pprint

proxy = xmlrpclib.ServerProxy('http://128.238.77.10:8000')

print "Listing all VMs..."
print proxy.xenapi.list_all_vms('rdj259@nyu.edu', 'Test123!')

print "Listing specific VM..."
pprint(proxy.xenapi.list_vm('rdj259@nyu.edu', 'Test123!', 'bt5-qemu14'))

print "Registering new VM..."
proxy.xenapi.register_vm('rdj259@nyu.edu', 'Test123!', '1_3_1', "3_1")  # <<studentid_courseid_vmid>>

print "Stopping vm if exists..."
proxy.xenapi.stop_vm('rdj259@nyu.edu', 'Test123!', '1_3_1')

print "Starting VM..."
vm = proxy.xenapi.start_vm('rdj259@nyu.edu', 'Test123!', '1_3_1')
pprint(vm)

print "Listing all VMs..."
print proxy.xenapi.list_all_vms('rdj259@nyu.edu', 'Test123!')

#print "Stopping created VM..."
#proxy.xenapi.stop_vm('rdj259@nyu.edu', 'Test123!', '1_3_1')

#print "Unregistering VM"
#proxy.xenapi.unregister_vm('rdj259@nyu.edu', 'Test123!', '1_3_1')

#print "Listing all VMs..."
#print proxy.xenapi.list_all_vms('rdj259@nyu.edu', 'Test123!')
