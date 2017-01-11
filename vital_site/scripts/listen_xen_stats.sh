#!/bin/bash

# this is called by upstart job on apache2 start - /etc/init/upstart/vital_listen_xen_stats.conf
# workon vital - instead point to virtualenv python installation
nohup /home/rdj259/.virtualenvs/vital/bin/python /home/rdj259/vital2.0/source/virtual_lab/vital_site/manage.py StartServerStatsCollection &