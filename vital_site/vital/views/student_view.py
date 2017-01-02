from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from ..models import Course, Registered_Course, Virtual_Machine, User_VM_Config, Available_Config, \
    User_Network_Configuration
from ..forms import Course_Registration_Form
from ..utils import audit, XenClient
import logging
from subprocess import Popen, PIPE
from django.db import transaction
from ..cron import clean_zombie_vms

logger = logging.getLogger(__name__)


@login_required(login_url='/vital/login/')
def registered_courses(request):
    """
    lists all registered courses for logged in user
    :param request: http request
    :return: registered courses page
    """
    logger.debug("In registered courses")
    #  reg_courses = Registered_Courses.objects.filter(user_id=request.user.id, course__status='ACTIVE')
    reg_courses = Registered_Course.objects.filter(user_id=request.user.id)
    message = ''
    if len(reg_courses) == 0:
        message = 'You have no registered courses'
    return render(request, 'vital/registered_courses.html', {'reg_courses': reg_courses, 'message':message})


@login_required(login_url='/vital/login/')
def course_vms(request, course_id):
    """
    lists all VMs of the selected course
    :param request: http request
    :param course_id: id of the selected course
    :return: course VMs page
    """
    logger.debug("in course vms")
    params = dict()
    virtual_machines = Virtual_Machine.objects.filter(course_id=course_id)
    for vm in virtual_machines:
        user_vm_configs = vm.user_vm_config_set.filter(user_id=request.user.id)
        if user_vm_configs is not None and not len(user_vm_configs) == 0:
            vm.state = 'R'
            user_vm_configs = vm.user_vm_config_set.filter(user_id=request.user.id)
            for config in user_vm_configs:
                if config.vm.id == vm.id:
                    vm.terminal_port = config.terminal_port
                    break
        else:
            vm.state = 'S'
    params['virtual_machines'] = virtual_machines
    params['course_id'] = course_id

    if not request.GET.get('message', '') == '':
        params['message'] = request.GET.get('message')

    return render(request, 'vital/course_vms.html', params)


def start_novnc(config, started_vm):
    """
    starts the novnc server for client to connect to
    :param config: AvailableConfig object to save vnc pid
    :param started_vm: object refering to the started VM
    :return: None
    """
    flag = True
    cnt = 0
    # hack to handle concurrent requests
    while flag:
        available_config = Available_Config.objects.filter(category='TERM_PORT').order_by('id')[0]
        locked_conf = Available_Config.objects.select_for_update().filter(id=available_config.id)
        cnt += 1
        if locked_conf is not None and len(locked_conf) > 0:
            val = locked_conf[0].value
            locked_conf.delete()
            cmd = 'sh /var/www/clone.com/interim/noVNC/utils/launch.sh --listen {} ' \
                  '--vnc {}:{}'.format(val, started_vm['xen_server'], started_vm['vnc_port'])
            logger.debug("start novnc - "+cmd)
            p = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
            config.no_vnc_pid = p.pid
            line = p.stdout.readline()
            if 'on port' in line:
                port = line[line.index('on port') + 7:].strip()
                config.terminal_port = port
                flag = False
        if cnt >= 100:
            raise Exception('Server busy : cannot start VM')


@login_required(login_url='/vital/login/')
def start_vm(request, course_id, vm_id):
    """
    starts the specified VM
    :param request: http request
    :param course_id: id of the selected course
    :param vm_id: id of the virtual machine
    :return: starts the VM and redirects ti Course VM page
    """
    config = User_VM_Config()
    try:
        with transaction.atomic():
            vm = Virtual_Machine.objects.get(pk=vm_id)
            config.vm = vm
            config.user_id = request.user.id
            # start vm with xen api which returns handle to the vm
            started_vm = XenClient().start_vm(request.user, course_id, vm_id)
            config.vnc_port = started_vm['vnc_port']
            config.xen_server = started_vm['xen_server']

            # run novnc launch script
            start_novnc(config, started_vm)
            config.save()
            return redirect('/vital/courses/' + course_id + '/vms?message=' + vm.name + ' VM started')
    except Virtual_Machine.DoesNotExist as e:
        logger.error(str(e))
        return redirect('/vital/courses/' + course_id + '/vms?message=Unable to start VM - ' + vm.name)
    except Exception as e:
        logger.error(str(e))
        if 'Connection refused' not in str(e).rstrip():
            XenClient().stop_vm(config.xen_server, request.user, course_id, vm_id)
            released_conf = Available_Config()
            released_conf.category = 'TERM_PORT'
            released_conf.value = config.terminal_port
            released_conf.save()
        return redirect('/vital/courses/' + course_id + '/vms?message=Unable to start VM - ' + vm.name)


def stop_vm(request, course_id, vm_id):
    """
    stops the specified VM
    :param request: http request
    :param course_id: id of the selected course
    :param vm_id: id of the virtual machine to stop
    :return: stops the VM and returns to Course VM page
    """
    vm = User_VM_Config.objects.get(user_id=request.user.id, vm_id=vm_id)

    cmd = 'kill ' + vm.no_vnc_pid
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    if not p.returncode == 0:
        if 'No such process' not in err.rstrip():
            raise Exception('ERROR : cannot stop the vm '
                            '\n Reason : %s' % err.rstrip())
    XenClient().stop_vm(vm.xen_server, request.user, course_id, vm_id)
    config = Available_Config()
    config.category = 'TERM_PORT'
    config.value = vm.terminal_port
    config.save()
    vm.delete()
    return redirect('/vital/courses/' + course_id + '/vms?message=VM stopped...')


@login_required(login_url='/vital/login/')
def rebase_vm(request, course_id, vm_id):
    """
    rebase the specified VM to initial state
    :param request: http request
    :param course_id: id of the selected course
    :param vm_id: if od the VM to be rebased
    :return: rebases VM and redirects to Course VMs page
    """
    logger.debug("In rebase vm")
    try:
        vm = User_VM_Config.objects.get(user_id=request.user.id, vm_id=vm_id)
        stop_vm(request, course_id, vm_id)
    except User_VM_Config.DoesNotExist as e:
        pass
    XenClient().rebase_vm(request.user, course_id, vm_id)
    return redirect('/vital/courses/' + course_id + '/vms?message=VM rebased to initial state..')


@login_required(login_url='/vital/login/')
def register_for_course(request):
    """
    creates necessary VMs for the specified course
    :param request: http request
    :return: creates the VM and redirects to Course VMs page
    """
    logger.debug("in register for course")
    error_message = ''
    if request.method == 'POST':
        form = Course_Registration_Form(request.POST)
        if form.is_valid():
            logger.debug(form.cleaned_data['course_registration_code']+"<>"+str(request.user.id)+"<>"+
                         str(request.user.is_faculty))
            try:
                with transaction.atomic():
                    course = Course.objects.get(registration_code=form.cleaned_data['course_registration_code'])
                    user = request.user
                    if len(Registered_Course.objects.filter(course_id=course.id, user_id=user.id)) > 0:
                        error_message = 'You have already registered for this course'
                    else:
                        if course.capacity > len(Registered_Course.objects.filter(course_id=course.id)) \
                                and course.status == 'ACTIVE':
                            XenClient().register_student_vms(request.user, course)
                            registered_course = Registered_Course(course_id=course.id, user_id=user.id)
                            registered_course.save()
                            audit(request, registered_course,
                                  'User ' + str(user.id) + ' registered for new course -' + str(course.id))
                            return redirect('/vital/courses/registered/')
                        else:
                            error_message = 'The course is either inactive or has reached its maximum student capacity.'
            except Course.DoesNotExist:
                error_message = 'Invalid registration code. Check again.'
    else:
        form = Course_Registration_Form()
    return render(request, 'vital/course_register.html', {'form': form, 'error_message': error_message})


@login_required(login_url='/vital/login/')
def unregister_from_course(request, course_id):
    """
    removes all VMs attached to a selected course and removes course finally from the users profile
    :param request: http request
    :param course_id: id of the course to be removed from user profile
    :return: removes the course and redirects to Course listing page
    """
    logger.debug("in course unregister")
    user = request.user
    course_to_remove = Registered_Course.objects.get(course_id=course_id, user_id=user.id)
    vms = User_VM_Config.objects.filter(user_id=request.user.id,
                                        vm_id__id=course_to_remove.course.virtual_machine_set.all())

    if len(vms) > 0:
        for vm_conf in vms:
            stop_vm(request,course_id, vm_conf.vm.id)

    XenClient().unregister_student_vms(request.user, course_to_remove.course)
    audit(request, course_to_remove, 'User '+str(user.id)+' unregistered from course -'+str(course_id))
    course_to_remove.delete()
    return redirect('/vital/courses/registered/')


# Remove after problem is fixed - or start the cron
@login_required(login_url='/vital/login/')
def fix_zombies(request):
    logger.debug('In fix zombie')
    if request.user.id == 2:
        clean_zombie_vms()
        return redirect('/vital/courses/registered/')
