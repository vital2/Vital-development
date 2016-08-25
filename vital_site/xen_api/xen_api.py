from subprocess import Popen, PIPE

import ConfigParser


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

    def stop_vm(self, vm_name):
        """
        stops the specified vm
        :param vm_name: name of the vm to be stopped
        """
        VirtualMachine(vm_name).shutdown()

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
            raise Exception('ERROR : cannot list the vm. \n Reason : %s' % err.rstrip())

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

    def register_vm(self, vm_name, student_id, course_id):
        """
        registers a new vm
        :param vm_name:
        :param student_id:
        :param course_id:
        """
        VirtualMachine(vm_name).register(student_id,course_id)

    def unregister_vm(self, vm_name):
        """
        registers a new vm
        :param vm_name:
        :param student_id:
        :param course_id:
        """
        VirtualMachine(vm_name).unregister()


class VirtualMachine:
    """
    References virtual machines which Xen maintains
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

    def shutdown(self):
        """
        this forcefully shuts down the virtual machine
        :param vm_name name of the vm to be shutdown
        """
        # xl destroy is used to forcefully shut down the vm
        # xl shutdown gracefully shuts down the vm but does not guarantee the shutdown
        cmd = 'xl destroy '+self.name
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        if not p.returncode == 0:
            # silently ignore if vm is already destroyed
            if 'invalid domain identifier' not in err.rstrip():
                raise Exception('ERROR : cannot stop the vm '
                                '\n Reason : %s' % err.rstrip())

    def register(self, student_id, course_id):
        """
        registers a new vm for the student - creates qcow and required conf files
        :param student_id: id of the student
        :param course_id: id of the course
        """

        cmd = 'cp ' + config.get("VMConfig", "VM_DSK_LOCATION") + '/clean/' + self.name + '.qcow ' +\
              config.get("VMConfig", "VM_DSK_LOCATION") + '/' + student_id + '_' + course_id + '_' +\
              self.name + '.qcow'
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        if not p.returncode == 0:
            raise Exception('ERROR : cannot register the vm - qcow '
                            '\n Reason : %s' % err.rstrip())

        cmd = 'cp ' + config.get("VMConfig", "VM_CONF_LOCATION") + '/clean/' + self.name + '.conf ' + \
              config.get("VMConfig", "VM_CONF_LOCATION") + '/' + student_id + '_' + course_id + '_' + \
              self.name + '.conf'
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        if not p.returncode == 0:
            raise Exception('ERROR : cannot register the vm - conf '
                            '\n Reason : %s' % err.rstrip())

        # TODO update conf file with required values
        f = open(config.get("VMConfig", "VM_CONF_LOCATION") + '/' + student_id + '_' + course_id + '_' +
                 self.name + '.conf', 'r')
        filedata = f.read()
        f.close()

        newdata = filedata.replace('<VM_NAME>', student_id + '_' + course_id + '_' + self.name)

        f = open(config.get("VMConfig", "VM_CONF_LOCATION") + '/' + student_id + '_' + course_id + '_' +
                 self.name + '.conf', 'w')
        f.write(newdata)
        f.close()

    def unregister(self):
        cmd = 'rm ' + config.get("VMConfig", "VM_DSK_LOCATION") + '/' + self.name + '.qcow'
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        if not p.returncode == 0:
            raise Exception('ERROR : cannot unregister the vm - qcow '
                            '\n Reason : %s' % err.rstrip())

        cmd = 'rm ' + config.get("VMConfig", "VM_CONF_LOCATION") + '/' + self.name + '.conf'
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        if not p.returncode == 0:
            raise Exception('ERROR : cannot unregister the vm - conf '
                            '\n Reason : %s' % err.rstrip())