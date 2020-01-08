from django.core.management.base import BaseCommand
import logging
import os
import re
import subprocess
from vital.models import Course, Registered_Course, User_Network_Configuration, Available_Config, User_VM_Config, Network_Configuration, Virtual_Machine, Course

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "removes a course completely by unregistering students and deleting the network config"

    def add_arguments(self, parser):
        parser.add_argument(
            '-c', '--course',
            action='store',
            dest='course_id',
            help='specify course id',
            required=True
        )

    def handle(self, *args, **options):
        try:
            course_id = options['course_id']
            course = Course.objects.get(id=course_id)
            print "Removing course: "+course.name+" (ID:" + str(course.id) + ")"
            print "Removing registered students"
            Registered_Course.objects.filter(course=course).delete()
            print "Removing registered user network configs"
            user_nets = User_Network_Configuration.objects.filter(course=course)
            for net in user_nets:
                conf = Available_Config()
                conf.category = 'MAC_ADDR'
                conf.value = net.mac_id
                conf.save()
                net.delete()
            print "Removing course network config"
            Network_Configuration.objects.filter(course=course).delete()
            print "Removing course virtual machines"
            Virtual_Machine.objects.filter(course=course).delete()
            Course.objects.get(id=course_id).delete()
            print course.name+" (ID:" + str(course.id) + ")"+" has been deleted"
        except Exception as  e:
            print(e)
            pass


        for files in os.listdir("/mnt/vlab-datastore/vital/vm_dsk/"):
            #print(files)
            if files.find(str(course_id)) == 3:
                files = "/mnt/vlab-datastore/vital/vm_dsk/" + files
                os.remove(files)

        for files in os.listdir("/mnt/vlab-datastore/vital/vm_conf/"):
            #print(files)
            if files.find(str(course_id)) == 3:
                files = "/mnt/vlab-datastore/vital/vm_conf/" + files
                os.remove(files)

        for files in os.listdir("/mnt/vlab-datastore/vital/vm_conf/clean/"):
            #print(files)
            if files.find(str(course_id)) == 0:
                files = "/mnt/vlab-datastore/vital/vm_conf/clean/" + files
                os.remove(files)

        for files in os.listdir("/mnt/vlab-datastore/vital/vm_dsk/clean/"):
            #print(files)
            if files.find(str(course_id)) == 0:
                files = "/mnt/vlab-datastore/vital/vm_dsk/clean/" + files
                os.remove(files)
        try:

            st = "/home/vlab_scp/vmnet_conf/vlab-natdhcp/Nat-" + str(course_id) + ".dchpd" 
            os.remove(st)
        except Exception as e:
            print(st+":"+str(e))
            pass

        remvlan = "vconfig rem bond0." + str(course_id)
        downvlan = "ip link set dev bond0."+ str(course_id) + " down"
        
        process = subprocess.Popen(downvlan.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        print(output)
        process = subprocess.Popen(remvlan.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        print(output)
        
        delrule = "iptables -D FORWARD -i bond0." + str(course_id) + " -s 10." + str(course_id) + ".1.0/24 -j REJECT"
        process = subprocess.Popen(delrule.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        print(output)
