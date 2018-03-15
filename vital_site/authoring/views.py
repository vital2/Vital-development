from django.shortcuts import render,redirect
import logging
import ConfigParser
from django.contrib.auth.decorators import login_required


config_ini = ConfigParser.ConfigParser()
config_ini.optionxform=str

config_ini.read("/home/vital/config.ini")
logger = logging.getLogger(__name__)

# Create your views here.


#@login_required(login_url='/vital/login/')
def index(request):
    return render(request, 'authoring/index.html')

