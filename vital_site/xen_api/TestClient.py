import xmlrpclib

proxy = xmlrpclib.ServerProxy('http://128.238.77.10:9000')
print 'public():', proxy.xenapi.public('richiedjohnson@yahoo.co.in', 'Test123!')

try:
    print 'public2():', proxy.xenapi.public2('richie', 'pass')
except Exception, err:
    print 'ERROR:', err
try:
    print 'private():', proxy.xenapi.private()
except Exception, err:
    print 'ERROR:', err
try:
    print 'public() without prefix:', proxy.public()
except Exception, err:
    print 'ERROR:', err