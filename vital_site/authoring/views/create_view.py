from django.shortcuts import render, redirect
import logging
from django import forms
import ConfigParser
from vital.utils import get_notification_message
from vital.models import Registered_Course, Course, Virtual_Machine, Virtual_Machine_Type, Network_Configuration
from ..forms import CreateCourseForm, CreateVmsForm, CreateNetworksForm
from django.utils.crypto import get_random_string
from django.http import HttpResponseRedirect, HttpResponse
#from datetime import datetime, date
import datetime

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
    created_courses = Course.objects.filter(course_owner=request.user.id)
    reg_courses = Course.objects.filter(id=request.user.id)
    # to display common notification messages like system maintenance plans on all pages
    request.session['notification'] = get_notification_message()
    message = ''
    if len(created_courses) == 0:
        message = 'You have no active courses'
    return render(request, 'authoring/course_home.html', {'created_courses': created_courses, 'reg_courses': reg_courses,
                  'message': message})


def course_create(request):
    logger.debug("in course create - " + request.method)
    error_message = ''
    if request.method == 'POST':
        form = CreateCourseForm(request.POST)
        if form.is_valid():
            course = Course()
            course.name = form.cleaned_data['course_name']
            course.course_number = form.cleaned_data['course_number']
            #course.start_date = form.cleaned_data['start_date']
            #course.created_date = datetime.date.today
            user_id = request.user.id
            course.course_owner = user_id
            reg_code = get_random_string(length=8)
            course.registration_code = reg_code
            course.save()
            request.session['course_id'] = course.id
            return redirect('/authoring/courses/addvms')
    else:
        form = CreateCourseForm()
    return render(request, 'authoring/course_create.html', {'form': form, 'error_message': error_message})


def course_add_vms(request):
    logger.debug("in course add vms")
    error_message = ''
    course_id = request.session.get('course_id', None)
    created_vms = Virtual_Machine.objects.filter(course=course_id)
    if request.method == 'POST':
        form = CreateVmsForm(request.POST)
        if form.is_valid():
            vm = Virtual_Machine()
            vm.course = Course.objects.get(id=course_id)
            vm.name = form.cleaned_data['vm_name']
            vm.type = form.cleaned_data['vm_type']
            vm.save()
            if request.POST.get("next"):
                return redirect('/authoring/courses/networking')
            else:
                form = CreateVmsForm()
    else:
        form = CreateVmsForm()
    return render(request, 'authoring/course_add_vms.html', {'created_vms': created_vms, 'form': form,
                                                             'error_message': error_message})


def course_networking(request):
    logger.debug("in course networking")
    error_message = ''
    course_id = request.session.get('course_id', None)
    created_nets = Network_Configuration.objects.filter(course=course_id)
    if request.method == 'POST':
        form = CreateNetworksForm(course_id, request.POST)
        if form.is_valid():
            net = Network_Configuration()
            net.name = form.cleaned_data['hub_name']
            net.course = Course.objects.get(id=course_id)
            net.virtual_machine = form.cleaned_data['hub_vms']
            net.interface = form.cleaned_data['vm_iface']
            net.save()
            if request.POST.get("next"):
                return redirect('/authoring/courses/summary')
            else:
                form = CreateNetworksForm(course_id)
    else:
        form = CreateNetworksForm(course_id)
    return render(request, 'authoring/course_networking.html', {'created_nets': created_nets,
                                                                'form': form, 'error_message': error_message})


def course_summary(request):
    logger.debug("in course summary")
    error_message = ''
    course_id = request.session.get('course_id', None)
    course_name = Course.objects.get(id=course_id)
    vms = Virtual_Machine.objects.filter(course=course_id)
    hubs = Network_Configuration.objects.filter(course=course_id)
    xen_servers = config_ini.get("Servers")
    logger.debug(xen_servers)
    if request.method == 'POST':
        logger.debug("activating course" + course_id)

    return render(request, 'authoring/course_summary.html', {'course_name': course_name, 'vms': vms, 'hubs': hubs,
                                                             'error_message': error_message})


def course_vm_setup(request):
    return HttpResponse('you are on the course vm setup page')


def course_destroy(request):
    return HttpResponse('you are on the course remove page')