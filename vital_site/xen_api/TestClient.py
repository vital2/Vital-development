import xmlrpclib
from pprint import pprint

proxy = xmlrpclib.ServerProxy('http://192.168.35.11:8000')

print "Listing all VMs..."
print proxy.xenapi.list_all_vms('rdj259@nyu.edu', 'pbkdf2_sha256$24000$rvI8ja8A8EVx$vvBZNpvNr72fBsmcNOJqIsKqrf9uyUM5PoLuivxbcoo=')

print "Registering new VM..."
proxy.xenapi.register_vm('rdj259@nyu.edu', 'pbkdf2_sha256$24000$rvI8ja8A8EVx$vvBZNpvNr72fBsmcNOJqIsKqrf9uyUM5PoLuivxbcoo=', '2_3_2', "3_2")  # <<studentid_courseid_vmid>>

print "Stopping vm if exists..."
proxy.xenapi.stop_vm('rdj259@nyu.edu', 'pbkdf2_sha256$24000$rvI8ja8A8EVx$vvBZNpvNr72fBsmcNOJqIsKqrf9uyUM5PoLuivxbcoo=', '2_3_2')

print "Starting VM..."
vm = proxy.xenapi.start_vm('rdj259@nyu.edu', 'pbkdf2_sha256$24000$rvI8ja8A8EVx$vvBZNpvNr72fBsmcNOJqIsKqrf9uyUM5PoLuivxbcoo=', '2_3_2')
pprint(vm)

print "Listing specific VM..."
pprint(proxy.xenapi.list_vm('rdj259@nyu.edu', 'pbkdf2_sha256$24000$rvI8ja8A8EVx$vvBZNpvNr72fBsmcNOJqIsKqrf9uyUM5PoLuivxbcoo=', '2_3_2'))

print "Stopping created VM..."
proxy.xenapi.stop_vm('rdj259@nyu.edu', 'pbkdf2_sha256$24000$rvI8ja8A8EVx$vvBZNpvNr72fBsmcNOJqIsKqrf9uyUM5PoLuivxbcoo=', '2_3_2')

print "Listing all VMs..."
print proxy.xenapi.list_all_vms('rdj259@nyu.edu', 'pbkdf2_sha256$24000$rvI8ja8A8EVx$vvBZNpvNr72fBsmcNOJqIsKqrf9uyUM5PoLuivxbcoo=')

print "Unregistering VM"
proxy.xenapi.unregister_vm('rdj259@nyu.edu', 'pbkdf2_sha256$24000$rvI8ja8A8EVx$vvBZNpvNr72fBsmcNOJqIsKqrf9uyUM5PoLuivxbcoo=', '2_3_2')

print "Listing all VMs..."
print proxy.xenapi.list_all_vms('rdj259@nyu.edu', 'pbkdf2_sha256$24000$rvI8ja8A8EVx$vvBZNpvNr72fBsmcNOJqIsKqrf9uyUM5PoLuivxbcoo=')
