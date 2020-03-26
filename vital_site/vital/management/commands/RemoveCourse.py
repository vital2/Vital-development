from django.core.management.base import BaseCommand
import logging
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
        course_id = options['course_id']
        course = Course.objects.get(id=course_id)
        print("Removing course: "+course.name+" (ID:" + str(course.id) + ")")
        print("Removing registered students")
        Registered_Course.objects.filter(course=course).delete()
        print("Removing registered user network configs")
        user_nets = User_Network_Configuration.objects.filter(course=course)
        for net in user_nets:
            conf = Available_Config()
            conf.category = 'MAC_ADDR'
            conf.value = net.mac_id
            conf.save()
            net.delete()
        print("Removing course network config")
        Network_Configuration.objects.filter(course=course).delete()
        print("Removing course virtual machines")
        Virtual_Machine.objects.filter(course=course).delete()
        Course.objects.get(id=course_id).delete()
        print(course.name+" (ID:" + str(course.id) + ")"+" has been deleted")
