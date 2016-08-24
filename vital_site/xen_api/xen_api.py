from subprocess import Popen, PIPE

import ConfigParser
from pprint import pprint


config = ConfigParser.ConfigParser()
config.read("/home/vlab/config.ini")


class XenAPI:
    """
    Provides api to xen operations
    """

    def __init__(self):
        pass

    def start_vm(self, vm_name):
        """
        starts specified virtual machine
        :param vm_name name of virtual machine
        """
        return VirtualMachine(vm_name).start()

    def list_all_vms(self):
        """
        lists all vms in the server (output of xl list)
        :return List of VirtualMachine with id, name, memory, vcpus, state, uptime
        """
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
            line = " ".join(line.split())
            val = line.split(" ")

            # creating VirtualMachine instances to return
            vm = VirtualMachine(val[0])
            vm.id = val[1]
            vm.memory = val[2]
            vm.vcpus = val[3]
            vm.state = val[4]
            vm.uptime = val[5]
            vms.append(vm)
        return vms

    def list_vm(self, vm_name):
        """
        lists specified virtual machine (output of xl list vm_name)
        :param vm_name name of virtual machine
        :return VirtualMachine with id, name, memory, vcpus, state, uptime
        """
        cmd = 'xl list '+vm_name
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        if not p.returncode == 0:
            raise Exception('ERROR : cannot start the vm. \n Reason : %s' % err.rstrip())

        output = out.split("\n")
        line = output[1]
        line = " ".join(line.split())
        val = line.strip().split(" ")

        # creating VirtualMachine instance to return
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
    """
    References virtual machines which Xen services
    """

    def __init__(self, name):
        self.name = name

    def start(self):
        """
        starts specified virtual machine
        :return: virtual machine stats with id, name, memory, vcpus, state, uptime, vnc_port
        """
        cmd = 'xl create ' + config.get("VMConfig", "VM_CONF_LOCATION") + '/' + self.name + '.conf'
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        if not p.returncode == 0:
            raise Exception('ERROR : cannot start the vm. \n Reason : %s' % err.rstrip())
        else:
            newvm = XenAPI().list_vm(self.name)
            # even though value of vnc port is set in the config file, if the port is already in use
            # by the vnc server, it allocates a new vnc port without throwing an error. this additional
            # step makes sure that we get the updated vnc-port
            cmd = 'xenstore-read /local/domain/'+newvm.id+'/console/vnc-port'
            p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
            out, err = p.communicate()
            if not p.returncode == 0:
                raise Exception('ERROR : cannot start the vm - error while getting vnc-port. '
                                '\n Reason : %s' % err.rstrip())
            newvm.vnc_port = out.rstrip()
            return newvm

    def shutdown(self, vm_name):
        """
        this forcefully shuts down the virtual machine
        :param vm_name name of the vm to be shutdown
        """
        # xl destroy is used to forcefully shut down the vm
        # xl shutdown gracefully shuts down the vm but does not guarantee the shutdown
        cmd = 'xl destroy '+vm_name
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()

# XenAPI().start_vm("bt5-qemu73")
print XenAPI().list_all_vms()
print XenAPI().list_vm('bt5-qemu14')
vm = XenAPI().start_vm('bt5-qemu73')
print vm.name+"<>"+vm.vnc_port
pprint(vars(vm))
