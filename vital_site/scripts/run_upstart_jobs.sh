#!/bin/bash

xens=$(psql -U postgres -d vital_db -t -c "SELECT x.name from vital_xen_server x where x.status='ACTIVE'")
set -f
array=(${xens// / })

for xen in "${array[@]}"
do
    ssh $xen
    systemctl start vital_on_xen_start.service
done

systemctl start vital_on_server_start.service

id=$1
/home/vital/vital2.0/source/virtual_lab/vital_site/scripts/create_nat_file.sh $id