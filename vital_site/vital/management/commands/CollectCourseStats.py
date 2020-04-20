from django.core.management.base import BaseCommand, CommandError
import logging
from django.utils import timezone
from vital.models import Course, Registered_Course, User_Network_Configuration, Available_Config, User_VM_Config
from django.utils.crypto import get_random_string
import ConfigParser
import os
import errno

logger = logging.getLogger(__name__)
config = ConfigParser.ConfigParser()
config.optionxform=str

# TODO change to common config file in shared location
config.read("/home/vital/config.ini")

class Command(BaseCommand):
    help = "Collect Stats for the Vital"

    def add_arguments(self, parser):
        parser.add_argument(
            '-c', '--course',
            action='store',
            dest='course_id',
            help='Specify course id',
            default='0'
        )
        parser.add_argument(
                '-a','--all',
                action='store_true', 
                help='Specify for all courses',
                default='False',
                dest='a'
                )

    def handle(self, *args, **options):
        
        if options['a']==True:
            total = 0 
            courseswithzeroreg = []
            print "\n\n"
            for course in Course.objects.all():
                print "Collecting stats for {} id: {}".format(course.name, course.id)
                print "\tCourse Number: {}".format(course.course_number)
                studentcount = len((Registered_Course.objects.filter(course=course)).values_list("user_id", flat=True))
                print "\tNo. of Students registered for {}: {}".format(course.name, studentcount)
                if studentcount == 0:
                    courseswithzeroreg.append(course.name)
                total = total + studentcount
                print "\n\n"
            print "Total No. of registerations: {}".format(total)
            print "\n\nFollowing Courses are not registered for any students this semester: "
            for name in courseswithzeroreg:
                print"\t * {}".format(name)

        elif options['course_id'] != 0:
            course_id = options['course_id']
            course = Course.objects.get(id=course_id)
            print "\n\nCollecting stats for {} id: {}".format(course.name, course.id)
            print "\tCourse Number: {}".format(course.course_number)
            studentcount = len((Registered_Course.objects.filter(course=course)).values_list("user_id", flat=True))
            print "\tNo. of Students registered for {}: {}\n".format(course.name, studentcount)
