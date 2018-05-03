from django.shortcuts import render, redirect, HttpResponse
import logging
from django import forms
import ConfigParser
from vital.utils import get_notification_message
from vital.models import Registered_Course, Course, Virtual_Machine, Virtual_Machine_Type, Network_Configuration
from ..forms import CreateCourseForm, CreateVmsForm, CreateNetworksForm
from django.utils.crypto import get_random_string
from django.http import HttpResponseRedirect, HttpResponse

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
    active_courses = Registered_Course.objects.filter(user_id=request.user.id, course__status='ACTIVE')

    # to display common notification messages like system maintenance plans on all pages
    request.session['notification'] = get_notification_message()
    message = ''
    if len(active_courses) == 0:
        message = 'You have no active courses'
    return render(request, 'authoring/course_home.html', {'active_courses': active_courses, 'message': message})


def course_create(request):
    logger.debug("in course create - " + request.method)
    error_message = ''
    if request.method == 'POST':
        form = CreateCourseForm(request.POST)
        if form.is_valid():
            course = Course()
            course.name = form.cleaned_data['course_name']
            course.course_number = form.cleaned_data['course_number']
            course.start_date = form.cleaned_data['start_date']
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
    if request.method == 'POST':
        form = CreateVmsForm(request.POST)
        if form.is_valid():
            vm = Virtual_Machine()
            course_id = request.session.get('course_id', None)
            vm.course = Course.objects.get(id=course_id)
            vm.name = form.cleaned_data['vm_name']
            vm.type = form.cleaned_data['vm_type']
            vm.save()
            return redirect('/authoring/courses/networking')
    else:
        form = CreateVmsForm()
    return render(request, 'authoring/course_add_vms.html', {'form': form, 'error_message': error_message})


def course_networking(request):
    logger.debug("in course networking")
    error_message = ''
    if request.method == 'POST':
        form = CreateNetworksForm(request.POST)
        course_id = request.session.get('course_id', None)
        #form.fields['hub_vms'] = forms.ModelChoiceField(Virtual_Machine.objects.filter(course=course_id))
        form.fields['hub_vms'].queryset = Virtual_Machine.objects.filter(course=course_id)
        if form.is_valid():
            net = Network_Configuration()
            net.name = form.cleaned_data['hub_name']
            net.course = course_id
            net.virtual_machine = form.cleaned_data['hub_vms']
            net.is_course_net = 'f'
            net.has_internet_access = 'f'
            net.save()
            return HttpResponse('form is valid')
    else:
        form = CreateNetworksForm()
    return render(request, 'authoring/course_networking.html', {'form': form, 'error_message': error_message})


def course_vm_setup(request):
    return HttpResponse('you are on the course vm setup page')


def course_destroy(request):
    return HttpResponse('you are on the course remove page')