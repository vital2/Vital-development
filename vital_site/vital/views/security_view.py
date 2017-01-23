from django.shortcuts import render, redirect, render_to_response
from django.contrib.auth import login as django_login, authenticate, logout as django_logout
from django.core.mail import send_mail
from django.http import HttpResponseNotAllowed
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from ..utils import XenClient, audit
from subprocess import Popen, PIPE


from ..forms import Registration_Form, User_Activation_Form, Authentication_Form, Reset_Password_Form, \
    Forgot_Password_Form
from ..models import VLAB_User, Allowed_Organization, User_VM_Config, Available_Config


import logging
import re
from random import randint


logger = logging.getLogger(__name__)


def register(request):
    logger.debug("in register")
    error_message = ''
    if request.method == 'POST':
        form = Registration_Form(request.POST)
        form.clean()
        if form.is_valid():
            user = form.save(commit=False)
            logger.debug(user)
            try:
                user = VLAB_User.objects.get(email=user.email)
                error_message = 'User is already registered.'
            except VLAB_User.DoesNotExist:
                suffix = re.search("@[\w.]+", user.email)
                logger.debug( "$$$$$$$$$$$$$$$$$$$$"+suffix.group())
                try:
                    allowed_org = Allowed_Organization.objects.get(email_suffix=suffix.group()[1:])
                except Allowed_Organization.DoesNotExist:
                    error_message = 'User organization not registered with Vital!'
                    return render(request, 'vital/user_registration.html', {'form': form, 'error_message':error_message})
                user.sftp_account = user.email[:user.email.find('@')]
                user.sftp_pass = user.password  # workaround to set sftp account
                user.set_password(user.password)  # hashes the password
                activation_code = randint(100000, 999999)
                user.activation_code = activation_code

                #TODO temporary fix until sftp issue solved
                if set('[~!@#$%^&*()_+{}":;\']+$').intersection(user.sftp_pass):
                    error_message = 'Special characters cannot be used in password'
                    return render(request, 'vital/user_registration.html',
                                  {'form': form, 'error_message': error_message})

                logger.debug("Creating SFTP account")
                cmd = 'sudo /home/rdj259/vital2.0/source/virtual_lab/vital_site/scripts/sftp_account.sh create '+ \
                      user.sftp_account+' '+user.sftp_pass + ' > /home/rdj259/vital2.0/log/sftp.log'
                p = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
                out, err = p.communicate()
                if not p.returncode == 0:
                    raise Exception('ERROR : cannot register sftp account. \n Reason : %s' % err.rstrip())
                logger.debug("SFTP account created")

                user.save()

                logger.debug("user registered : "+ user.email)
                send_mail('Activation mail', 'Hi '+user.first_name+',\r\n\n Welcome to Vital. Please use activation '
                                             'code : '+str(activation_code)+' for activating your account.\r\n\nVital',
                          'no-reply-vital@nyu.edu', [user.email], fail_silently=False)
                logger.debug("user activation email sent to "+ user.email)
                form = User_Activation_Form(initial={'user_email': user.email})
                return render(request, 'vital/user_registration_validate.html', {'message': 'User has been registered. '
                                                                                            + 'Please check your mail('
                                                                                            + user.email+') for ' +
                                                                                            'activation code',
                                                                                 'form': form})
    else:
        form = Registration_Form()

    return render(request, 'vital/user_registration.html', {'form': form, 'error_message':error_message})


def activate(request):
    logger.debug("in activate")
    message = ''
    if request.method == 'POST':
        form = User_Activation_Form(request.POST)
        if form.is_valid():
            logger.debug(form.cleaned_data['user_email']+'-'+form.cleaned_data['code'])
            try:
                user = VLAB_User.objects.get(email=form.cleaned_data['user_email'])
                if not user.is_active:
                    if user.activation_code == int(form.cleaned_data['code']):
                        user.is_active = True
                        user.activation_code = None
                        user.save()
                        user.backend = 'django.contrib.auth.backends.ModelBackend'
                        django_login(request, user)
                        #audit(request, 'Activated user')
                        send_mail('Welcome to Vital',
                                  'Hi ' + user.first_name + ',\r\n\n Welcome to Vital. Your account has been activated. '
                                                            'Please follow instructions '
                                                            'from your instructor to access the course VMs. '
                                                            '\r\nYour SFTP account is '+user.sftp_account+' and password'
                                                            ' is the same as vital\r\n\nVital',
                                  'no-reply-vital@nyu.edu', [user.email], fail_silently=False)
                        logger.debug('activated..'+user.email)
                        form = Authentication_Form()
                        # return render(request, 'vital/login.html', {'form': form })
                        return redirect('/vital')
                    else:
                        message = 'Please check your activation code'
                else:
                    message = 'User is already active'
                    form = Authentication_Form()
                    return render(request, 'vital/login.html', {'form': form, 'error_message': message })
            except (VLAB_User.DoesNotExist, ValueError) as e:
                message = 'Please check your activation code'
                logger.debug('cannot be activated..'+form.cleaned_data['user_email'])
                logger.error(e)
        else:
            logger.debug(form.errors)
        return render(request, 'vital/user_registration_validate.html', {'form': form, 'error_message':message})
    else:
        return HttpResponseNotAllowed('Only POST here')


def reset_password(request):
    logger.debug("in reset password")
    error_message = ''
    if request.method == 'POST':
        form = Reset_Password_Form(request.POST)
        if form.is_valid():
            logger.debug(">>>>>>>>>>>>>>>>>>"+str(request.user))
            # TODO temporary fix until sftp issue solved
            if set('[~!@#$%^&*()_+{}":;\']+$').intersection(form.cleaned_data['password']):
                error_message = 'Special characters cannot be used in password'
                return render(request, 'vital/user_reset_password.html',
                              {'form': form, 'error_message': error_message})
            if not request.user.is_anonymous():
                user = VLAB_User.objects.get(email=request.user.email)
                user.set_password(form.cleaned_data['password'])
                user.sftp_pass = form.cleaned_data['password']

                logger.debug("Resetting SFTP account")
                cmd = 'sudo /home/rdj259/vital2.0/source/virtual_lab/vital_site/scripts/sftp_account.sh resetpass ' + \
                      user.sftp_account + ' ' + user.sftp_pass
                p = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
                out, err = p.communicate()
                if not p.returncode == 0:
                    raise Exception('ERROR : cannot register sftp account. \n Reason : %s' % err.rstrip())
                logger.debug("SFTP account reset")

                user.save()
                update_session_auth_hash(request, user)
                return redirect('/vital')  # change here to home page
            else:
                logger.debug(form.cleaned_data['user_email']+'-'+form.cleaned_data['activation_code'])
                user = VLAB_User.objects.get(email=form.cleaned_data['user_email'])
                if user.activation_code == int(form.cleaned_data['activation_code']):
                    user.set_password(form.cleaned_data['password'])
                    user.sftp_pass = form.cleaned_data['password']
                    user.activation_code=None

                    logger.debug("Resetting SFTP account")
                    cmd = 'sudo /home/rdj259/vital2.0/source/virtual_lab/vital_site/scripts/sftp_account.sh resetpass ' + \
                          user.sftp_account + ' ' + user.sftp_pass
                    p = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
                    out, err = p.communicate()
                    if not p.returncode == 0:
                        raise Exception('ERROR : cannot register sftp account. \n Reason : %s' % err.rstrip())
                    logger.debug("SFTP account reset")

                    user.save()
                    update_session_auth_hash(request, user)
                    return redirect('/vital')  # change here to home page
                else:
                    error_message = 'Please use the link sent to you in your email'
    else:
        user_email = request.GET.get('user_email', 'x')
        activation_code = request.GET.get('activation_code', 'x')
        form = Reset_Password_Form(initial={'user_email': user_email, 'activation_code':activation_code})
    return render(request, 'vital/user_reset_password.html', {'form': form, 'error_message': error_message})


def forgot_password(request):
    logger.debug("in forgot password")
    message = ''
    if request.method == 'POST':
        form = Forgot_Password_Form(request.POST)
        if form.is_valid():
            try:
                user = VLAB_User.objects.get(email=form.cleaned_data['email'])
                activation_code = randint(100000, 999999)
                user.activation_code = activation_code
                user.save()
                send_mail('Password reset mail', 'Hi '+user.first_name+',\r\n\n Please copy the following link to '
                                                                       'reset your password to your browser. '
                                                                       'http://vital-dev2.poly.edu/'
                                                                       'vital/users/reset-password?user_email='
                          + user.email+'&activation_code='+str(activation_code)
                          + '.\r\n\nVital', 'no-reply-vital@nyu.edu',
                          [user.email], fail_silently=False)
            except VLAB_User.DoesNotExist:
                logger.debug('Cannot find requested email -'+form.cleaned_data['email'])
            message = "Email with reset password instructions is on the way"
    else:
        form = Forgot_Password_Form()
    return render(request, 'vital/forgot_password.html', {'form': form, 'message': message})


def login(request):
    logger.debug("in login")
    error_message = ''
    if request.method == 'POST':
        logger.debug("in login POST")
        form = Authentication_Form(request.POST)
        if form.is_valid():
            logger.debug(form.cleaned_data['email']+'<>'+form.cleaned_data['password'])
            user = authenticate(email=form.cleaned_data['email'], password=form.cleaned_data['password'])
            if user is not None:
                if user.is_active:
                    django_login(request, user)
                    audit(request, 'User logged in')
                    return redirect('/vital')
                else:
                    form = User_Activation_Form(initial={'user_email': user.email})
                    return render(request, 'vital/user_registration_validate.html', {'message': 'User is not active. ' +
                                                                                        'Please check your mail(' +
                                                                                        user.email+') for ' +
                                                                                        'activation code',
                                                                             'form': form})
            else:
                error_message = 'Login failed! Check your username and password.'
        else:
            error_message = 'Login failed! Check your username and password.'
    else:
        form = Authentication_Form()
    return render(request, 'vital/login.html', {'form': form, 'error_message': error_message})


def logout(request):
    logger.debug("in logout")
    logger.debug(">>>>>>>>>>>>>>>>>>" + str(request.user))
    audit(request, 'User logged out')
    django_logout(request)
    return redirect('/vital/login')


def stop_vms_during_logout(user):
    # this is called from logout signal
    logger.debug(">>>>>>>>>>>>>>>>>>" + str(user.id))
    user_vms = User_VM_Config.objects.filter(user_id=user.id)
    for user_vm in user_vms:
        vm = user_vm.vm
        cmd = 'kill ' + user_vm.no_vnc_pid
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        if not p.returncode == 0:
            if 'No such process' not in err.rstrip():
                raise Exception('ERROR : cannot stop the vm '
                                '\n Reason : %s' % err.rstrip())
        XenClient().stop_vm(user_vm.xen_server, user, vm.course.id, vm.id)
        config = Available_Config()
        config.category = 'TERM_PORT'
        config.value = user_vm.terminal_port
        config.save()
        user_vm.delete()


@login_required(login_url='/vital/login/')
def index(request):
    logger.debug("In index")
    user = request.user
    if not user.is_faculty and not user.is_admin:
        return redirect('/vital/courses/registered')  # change here to home page
    elif user.is_faculty:
        logger.debug('user is a faculty')
        return redirect('/vital/courses/advising')  # change here to home page
    else:
        logger.debug('user is admin')

