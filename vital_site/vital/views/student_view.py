from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from ..models import Course, Registered_Course, Virtual_Machine, User_VM_Config, Available_Config, \
    User_Network_Configuration
from ..forms import Course_Registration_Form
from ..utils import audit, XenClient, get_notification_message
import logging
from subprocess import Popen, PIPE
from django.db import transaction
import ConfigParser

logger = logging.getLogger(__name__)
config_ini = ConfigParser.ConfigParser()
config_ini.optionxform=str

# TODO change to common config file in shared location
config_ini.read("/home/rdj259/config.ini")


@login_required(login_url='/vital/login/')
def registered_courses(request):
    """
    lists all registered courses for logged in user
    :param request: http request
    :return: registered courses page
    """
    logger.debug("In registered courses")
    reg_courses = Registered_Course.objects.filter(user_id=request.user.id, course__status='ACTIVE')
    # reg_courses = Registered_Course.objects.filter(user_id=request.user.id)

    # to display common notification messages like system maintenance plans on all pages
    request.session['notification'] = get_notification_message()
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
    server_name = config_ini.get('VITAL', 'SERVER_NAME')
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
    params['server_name'] = server_name

    if not request.GET.get('message', '') == '':
        params['message'] = request.GET.get('message')

    return render(request, 'vital/course_vms.html', params)


@login_required(login_url='/vital/login/')
def console(request, vm_id):
    """
    fetches terminal port and server name for novnc console
    :param request: http request
    :param vm_id: id of the selected vm
    :return: port and servername
    """
    server_name = config_ini.get('VITAL', 'SERVER_NAME')
    vm = Virtual_Machine.objects.get(id=vm_id)
    user_vm_config = vm.user_vm_config_set.get(user_id=request.user.id)
    return render(request, 'vital/console.html', {"server_name":server_name, "terminal_port":user_vm_config.terminal_port})


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
            launch_script = config_ini.get("VITAL", "NOVNC_LAUNCH_SCRIPT")
            cmd = 'sh '+launch_script+' --listen {} ' \
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
    logger.debug("starting vm - " + str(request.user.id)+'_'+course_id+'_'+vm_id)
    config = User_VM_Config()
    started_vm = None
    vm = None
    try:
        vm = Virtual_Machine.objects.get(pk=vm_id)
        audit(request, 'Starting Virtual machine ' + str(vm.name))
        with transaction.atomic():
            config.vm = vm
            config.user_id = request.user.id
            # start vm with xen api which returns handle to the vm
            started_vm = XenClient().start_vm(request.user, course_id, vm_id)
            config.vnc_port = started_vm['vnc_port']
            config.xen_server = started_vm['xen_server']

            # run novnc launch script
            start_novnc(config, started_vm)
            config.save()
            audit(request, 'Started Virtual machine ' + str(vm.name))
            return redirect('/vital/courses/' + course_id + '/vms?message=' + vm.name + ' VM started')
    except Virtual_Machine.DoesNotExist as e:
        logger.error(str(e))
        audit(request, 'Error starting Virtual machine ' + str(vm_id) + '( Does not exist )')
        return redirect('/vital/courses/' + course_id + '/vms?message=Unable to start VM - ' + vm.name)
    except Exception as e:
        logger.error(str(e))
        audit(request, 'Error starting Virtual machine ' + str(vm.name) + '( ' + e.message + ' )')
        if 'Connection refused' not in str(e).rstrip() or started_vm is not None:
            XenClient().stop_vm(started_vm['xen_server'], request.user, course_id, vm_id)
        return redirect('/vital/courses/' + course_id + '/vms?message=Unable to start VM - ' + vm.name)


@login_required(login_url='/vital/login/')
def stop_vm(request, course_id, vm_id):
    """
    stops the specified VM
    :param request: http request
    :param course_id: id of the selected course
    :param vm_id: id of the virtual machine to stop
    :return: stops the VM and returns to Course VM page
    """
    logger.debug("stopping vm - " + str(request.user.id) + '_' + course_id + '_' + vm_id)
    virtual_machine = Virtual_Machine.objects.get(pk=vm_id)
    audit(request, 'Stopping Virtual machine ' + str(virtual_machine.name))
    vm = User_VM_Config.objects.get(user_id=request.user.id, vm_id=vm_id)

    cmd = 'kill ' + vm.no_vnc_pid
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    if not p.returncode == 0:
        if 'No such process' not in err.rstrip():
            audit(request, 'Error stopping Virtual machine ' + str(virtual_machine.name) +
                  '(' + err.rstrip() + ')')
            raise Exception('ERROR : cannot stop the vm '
                            '\n Reason : %s' % err.rstrip())
    try:
        XenClient().stop_vm(vm.xen_server, request.user, course_id, vm_id)
        config = Available_Config()
        config.category = 'TERM_PORT'
        config.value = vm.terminal_port
        config.save()
        vm.delete()
        audit(request, 'Stopped Virtual machine ' + str(virtual_machine.name))
        return redirect('/vital/courses/' + course_id + '/vms?message=VM stopped...')
    except Exception as e:
        audit(request, 'Error stopping Virtual machine ' + str(virtual_machine.name)+'('+e.message+')')
        raise e


@login_required(login_url='/vital/login/')
def rebase_vm(request, course_id, vm_id):
    """
    rebase the specified VM to initial state
    :param request: http request
    :param course_id: id of the selected course
    :param vm_id: if od the VM to be rebased
    :return: rebases VM and redirects to Course VMs page
    """
    logger.debug("rebasing vm - " + str(request.user.id) + '_' + course_id + '_' + vm_id)
    virtual_machine = Virtual_Machine.objects.get(pk=vm_id)
    audit(request, 'Re-imaging Virtual machine ' + str(virtual_machine.name))
    try:
        vm = User_VM_Config.objects.get(user_id=request.user.id, vm_id=vm_id)
        stop_vm(request, course_id, vm_id)
    except User_VM_Config.DoesNotExist as e:
        pass
    try:
        XenClient().rebase_vm(request.user, course_id, vm_id)
        audit(request, 'Re-imaged Virtual machine ' + str(virtual_machine.name))
    except Exception as e:
        audit(request, 'Error re-imaged Virtual machine ' + str(virtual_machine.name))
        raise e
    return redirect('/vital/courses/' + course_id + '/vms?message=VM rebased to initial state..')


@login_required(login_url='/vital/login/')
def register_for_course(request):
    """
    creates necessary VMs for the specified course
    :param request: http request
    :return: creates the VM and redirects to Course VMs page
    """
    logger.debug("in register for course - user_id:"+str(request.user.id))
    error_message = ''
    if request.method == 'POST':
        form = Course_Registration_Form(request.POST)
        if form.is_valid():
            logger.debug(form.cleaned_data['course_registration_code']+"<>"+str(request.user.id)+"<>"+
                         str(request.user.is_faculty))
            try:
                course = Course.objects.get(registration_code=form.cleaned_data['course_registration_code'])
                user = request.user
                audit(request, 'Registering for course ' + str(course.name))
                with transaction.atomic():
                    if len(Registered_Course.objects.filter(course_id=course.id, user_id=user.id)) > 0:
                        error_message = 'You have already registered for this course'
                    else:
                        if course.capacity > len(Registered_Course.objects.filter(course_id=course.id)) \
                                and course.status == 'ACTIVE':
                            XenClient().register_student_vms(request.user, course)
                            registered_course = Registered_Course(course_id=course.id, user_id=user.id)
                            registered_course.save()
                            audit(request, 'Registered for course ' + str(course.name))
                            return redirect('/vital/courses/registered/')
                        else:
                            audit(request, 'Error registering for course ' + str(course.name) + ' (Inactive/Capacity Full)')
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
    logger.debug("in course unregister- user_id:"+str(request.user.id))
    course = Course.objects.get(id=course_id)
    audit(request, 'Un-registering from course ' + str(course.name))

    try:
        user = request.user
        course_to_remove = Registered_Course.objects.get(course_id=course_id, user_id=user.id)
        vms = User_VM_Config.objects.filter(user_id=request.user.id,
                                            vm_id__in=course_to_remove.course.virtual_machine_set.all())

        if len(vms) > 0:
            for vm_conf in vms:
                stop_vm(request, course_id, vm_conf.vm.id)

        XenClient().unregister_student_vms(request.user, course_to_remove.course)
        audit(request, 'Un-registered from course ' + str(course.name))
        course_to_remove.delete()
        return redirect('/vital/courses/registered/')
    except Exception as e:
        audit(request, 'Error while Un-registering from course ' + str(course.name)+' ('+e.message+')')
        raise e
