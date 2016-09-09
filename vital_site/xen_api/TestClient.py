import xmlrpclib
from pprint import pprint

proxy = xmlrpclib.ServerProxy('http://128.238.77.10:8000')

print "Listing all VMs..."
print proxy.xenapi.list_all_vms('rdj259@nyu.edu', 'pbkdf2_sha256$24000$WK1SdV4Vx29M$kwlqioZRM2LGlbBo0nRGyFUoZQnEke84jKaOzIMaZ64=')

print "Listing specific VM..."
pprint(proxy.xenapi.list_vm('rdj259@nyu.edu', 'pbkdf2_sha256$24000$WK1SdV4Vx29M$kwlqioZRM2LGlbBo0nRGyFUoZQnEke84jKaOzIMaZ64=', 'Domain-0'))

print "Registering new VM..."
proxy.xenapi.register_vm('rdj259@nyu.edu', 'pbkdf2_sha256$24000$WK1SdV4Vx29M$kwlqioZRM2LGlbBo0nRGyFUoZQnEke84jKaOzIMaZ64=', '1_2_1', "2_1")  # <<studentid_courseid_vmid>>

print "Stopping vm if exists..."
proxy.xenapi.stop_vm('rdj259@nyu.edu', 'pbkdf2_sha256$24000$WK1SdV4Vx29M$kwlqioZRM2LGlbBo0nRGyFUoZQnEke84jKaOzIMaZ64=', '1_2_1')

print "Starting VM..."
vm = proxy.xenapi.start_vm('rdj259@nyu.edu', 'pbkdf2_sha256$24000$WK1SdV4Vx29M$kwlqioZRM2LGlbBo0nRGyFUoZQnEke84jKaOzIMaZ64=', '1_2_1')
pprint(vm)

print "Listing all VMs..."
print proxy.xenapi.list_all_vms('rdj259@nyu.edu', 'pbkdf2_sha256$24000$WK1SdV4Vx29M$kwlqioZRM2LGlbBo0nRGyFUoZQnEke84jKaOzIMaZ64=')

print "Stopping created VM..."
proxy.xenapi.stop_vm('rdj259@nyu.edu', 'pbkdf2_sha256$24000$WK1SdV4Vx29M$kwlqioZRM2LGlbBo0nRGyFUoZQnEke84jKaOzIMaZ64=', '1_2_1')

print "Unregistering VM"
proxy.xenapi.unregister_vm('rdj259@nyu.edu', 'pbkdf2_sha256$24000$WK1SdV4Vx29M$kwlqioZRM2LGlbBo0nRGyFUoZQnEke84jKaOzIMaZ64=', '1_2_1')

print "Listing all VMs..."
print proxy.xenapi.list_all_vms('rdj259@nyu.edu', 'pbkdf2_sha256$24000$WK1SdV4Vx29M$kwlqioZRM2LGlbBo0nRGyFUoZQnEke84jKaOzIMaZ64=')
