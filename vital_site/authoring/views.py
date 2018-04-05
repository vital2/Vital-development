from django.shortcuts import render, redirect, HttpResponse
import logging
import ConfigParser
from vital.utils import get_notification_message
from django.apps import apps


logger = logging.getLogger(__name__)
config_ini = ConfigParser.ConfigParser()
config_ini.optionxform = str

# TODO change to common config file in shared location
config_ini.read("/home/vital/config.ini")


def index(request):
    return redirect('/authoring/courses/home/')


def course_home(request):
    """
    lists all active courses for faculty
    :param request: http request
    :return: active courses page
    """
    logger.debug("In course home")
    reg_courses = apps.get_model('Registered_Course')
    active_courses = reg_courses.objects.filter(user_id=request.user.id, course__status='ACTIVE')

    # to display common notification messages like system maintenance plans on all pages
    request.session['notification'] = get_notification_message()
    message = ''
    if len(active_courses) == 0:
        message = 'You have no active courses'
    return render(request, 'authoring/course_home.html', {'active_courses': active_courses, 'message':message})


def course_create(request):
    return HttpResponse('you are on the course creation page')


def course_vm_setup(request):
    return HttpResponse('you are on the course vm setup page')


def course_destroy(request):
    return HttpResponse('you are on the course remove page')