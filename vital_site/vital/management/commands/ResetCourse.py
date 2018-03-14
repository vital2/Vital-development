from django.core.management.base import BaseCommand, CommandError
import logging
from django.utils import timezone
from vital.models import Course, Registered_Course, User_Network_Configuration, Available_Config, User_VM_Config
from django.utils.crypto import get_random_string

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "resets a course to remove all students and generate a new registration code"

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
        print "Removing course: "+course.name+" (ID:"+ str(course.id) +")"
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
        print "Setting new registration code"
        reg_code = get_random_string(length=8)
        course.registration_code = reg_code
        course.save()
        print "The course has been reset. The new registration code is "+reg_code