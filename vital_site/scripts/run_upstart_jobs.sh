#!/bin/bash

xens=

for xen in xens
do
    ssh xen
    systemctl start vital_on_xen_start.service
done

systemctl start vital_on_server_start.service

id=
/home/vital/vital2.0/source/virtual_lab/vital_site/scripts/create_nat_file.sh $id