from subprocess import Popen, PIPE

import ConfigParser


config = ConfigParser.ConfigParser()
config.read("/home/vlab/config.ini")


class XenAPI:

    def __init__(self):
        pass

    def start_vm(self, vm_name):
        # subprocess.call('xl create '+vm_name+".conf", shell=True)
        cmd = 'xl create '+config.get("VMConfig", "VM_CONF_LOCATION")+'/'+vm_name+'.conf'
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        print "Return code: ", p.returncode
        print '>'*80
        print out.rstrip()
        print '>' * 80
        print err.rstrip()
        if not p.returncode == 0:
            raise Exception('ERROR : cannot start the vm. \n Reason : %s' % err.rstrip())

    def check_if_port_is_used(self):
        pass

    def server_stats(self):
        pass

XenAPI().start_vm("bt5-qemu73")