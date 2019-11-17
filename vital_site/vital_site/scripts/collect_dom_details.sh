#!/bin/bash

# this is called by systemd on apache2 start - vital_collect_dom_details.service
# workon vital - instead point to virtualenv python installation
/home/vital/.virtualenvs/vital/bin/python /home/vital/vital2.0/source/virtual_lab/vital_site/manage.py CollectXenDomDetails
