from django.shortcuts import render, redirect, render_to_response
from django.contrib.auth import login as django_login, authenticate, logout as django_logout
from django.core.mail import send_mail
from django.http import HttpResponseNotAllowed
from django.template import RequestContext
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required

from ..forms import Registration_Form, User_Activation_Form, Authentication_Form, Reset_Password_Form, \
    Forgot_Password_Form
from ..models import VLAB_User
from ..models import Allowed_Organization

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
                user.set_password(user.password)  # hashes the password
                activation_code = randint(100000, 999999)
                user.activation_code = activation_code
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
                        update_session_auth_hash(request, user)
                        logger.debug('activated..'+user.email)
                        form = Authentication_Form()
                        #return render(request, 'vital/login.html', {'form': form })
                        return redirect('/vital')
                    else:
                        message = 'Please check your activation code'
                else:
                    message = 'User is already active'
                    form = Authentication_Form()
                    return render(request, 'vital/login.html', {'form': form })
            except VLAB_User.DoesNotExist as e:
                message = 'Please check your activation code'
                logger.debug('cannot be activated..'+form.cleaned_data['user_email'])
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
            if not request.user.is_anonymous():
                user = VLAB_User.objects.get(email=request.user.email)
                user.set_password(form.cleaned_data['password'])
                user.save()
                update_session_auth_hash(request, user)
                return redirect('/vital')  # change here to home page
            else:
                logger.debug(form.cleaned_data['user_email']+'-'+form.cleaned_data['activation_code'])
                user = VLAB_User.objects.get(email=form.cleaned_data['user_email'])
                if user.activation_code == int(form.cleaned_data['activation_code']):
                    user.set_password(form.cleaned_data['password'])
                    user.activation_code=None
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
    django_logout(request)
    return redirect('/vital/login')


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

