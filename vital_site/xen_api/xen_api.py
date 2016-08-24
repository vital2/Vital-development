from subprocess import Popen, PIPE


class XenAPI:

    def __init__(self):
        pass

    def start_vm(self, vm_name):
        # subprocess.call('xl create '+vm_name+".conf", shell=True)
        cmd = "ls -l ~/"
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        print "Return code: ", p.returncode
        print out.rstrip()
        #print err.rstrip()

    def check_if_port_is_used(self):
        pass

    def server_stats(self):
        pass

XenAPI().start_vm("bt5")