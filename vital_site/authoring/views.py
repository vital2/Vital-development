from django.shortcuts import render, redirect, HttpResponse
import logging
import ConfigParser

logger = logging.getLogger(__name__)
config_ini = ConfigParser.ConfigParser()
config_ini.optionxform = str

# TODO change to common config file in shared location
config_ini.read("/home/vital/config.ini")


def index(request):
    return render(request, 'authoring/index.html')
