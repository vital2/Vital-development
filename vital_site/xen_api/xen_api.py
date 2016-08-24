from subprocess import Popen, PIPE

import ConfigParser


config = ConfigParser.ConfigParser()
config.read("/home/vlab/config.ini")


class XenAPI:
    """ Provides api to xen operations """

    def __init__(self):
        pass

    def start_vm(self, vm_name):
        VirtualMachine(vm_name).start()

    def list_vms(self):
        cmd = 'xl list'
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        if not p.returncode == 0:
            raise Exception('ERROR : cannot start the vm. \n Reason : %s' % err.rstrip())

        for line in out.split("\n"):
            val = line.strip().split("\t")
            print val

        # print "Return code: ", p.returncode
        # print '>'*80
        # print out.rstrip()
        # print '>' * 80
        # print err.rstrip()

    def server_stats(self):
        pass


class VirtualMachine:
    """ References virtual machines which Xen services """

    def __init__(self, name):
        self.name = name

    def start(self):
        cmd = 'xl create ' + config.get("VMConfig", "VM_CONF_LOCATION") + '/' + vm_name + '.conf'
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        if not p.returncode == 0:
            raise Exception('ERROR : cannot start the vm. \n Reason : %s' % err.rstrip())
        else:
            return self


# XenAPI().start_vm("bt5-qemu73")
XenAPI().list_vms()