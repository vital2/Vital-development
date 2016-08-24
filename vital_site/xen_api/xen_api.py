from subprocess import Popen, PIPE

import ConfigParser


config = ConfigParser.ConfigParser()
config.read("/home/vlab/config.ini")


class XenAPI:
    """ Provides api to xen operations """

    def __init__(self):
        pass

    def start_vm(self, vm_name):
        """ starts specified virtual machine """
        VirtualMachine(vm_name).start()

    def list_all_vms(self):
        """ lists all vms in the server """
        cmd = 'xl list'
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        if not p.returncode == 0:
            raise Exception('ERROR : cannot start the vm. \n Reason : %s' % err.rstrip())

        vms = []
        output = out.strip().split("\n")
        for i in range(1, len(output)):
            # removing first line
            line = output[i]
            print line
            line = " ".join(line.split())
            print line
            val = line.strip().split(" ")
            print val
            vm = VirtualMachine(val[0])
            vm.id = val[1]
            vm.memory = val[2]
            vm.vcpus = val[3]
            vm.state = val[4]
            vm.uptime = val[5]
            vms.append(vm)
        return vms
        # print "Return code: ", p.returncode
        # print '>'*80
        # print out.rstrip()
        # print '>' * 80
        # print err.rstrip()

    def list_vm(self, vm_name):
        """ lists specified virtual machine """
        cmd = 'xl list'
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        if not p.returncode == 0:
            raise Exception('ERROR : cannot start the vm. \n Reason : %s' % err.rstrip())

        output = out.split("\n")
        line = output[1]
        line = " ".join(line.split())
        val = line.strip().split(" ")
        vm = VirtualMachine(val[0])
        vm.id = val[1]
        vm.memory = val[2]
        vm.vcpus = val[3]
        vm.state = val[4]
        vm.uptime = val[5]
        return vm

    def server_stats(self):
        pass


class VirtualMachine:
    """ References virtual machines which Xen services """

    def __init__(self, name):
        self.name = name

    def start(self):
        cmd = 'xl create ' + config.get("VMConfig", "VM_CONF_LOCATION") + '/' + self.name + '.conf'
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        if not p.returncode == 0:
            raise Exception('ERROR : cannot start the vm. \n Reason : %s' % err.rstrip())
        else:
            return self


# XenAPI().start_vm("bt5-qemu73")
print XenAPI().list_all_vms()
print XenAPI().list_vm('bt5-qemu14')
