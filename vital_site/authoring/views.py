from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ..models import Course, Registered_Course, Virtual_Machine, User_VM_Config, Available_Config, \
    User_Network_Configuration
from ..forms import Course_Registration_Form
from ..utils import audit, XenClient, get_notification_message
import logging
import ConfigParser

logger = logging.getLogger(__name__)
config_ini = ConfigParser.ConfigParser()
config_ini.optionxform = str

# TODO change to common config file in shared location
config_ini.read("/home/vital/config.ini")


def index(request):
    return render(request, '/authoring/index.html')
