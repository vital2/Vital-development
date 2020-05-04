#!/bin/bash

# This is called from upstart job /etc/init/on_server_start.conf
# postgres init script modified for this. similar to http://blog.systemed.net/post/6

# mounts glusterfs
# mount -t glusterfs gusterfs1-dev:volume1 /mnt/vlab-datastore
# mount -t glusterfs Vlab-gluster1:/vlab /mnt/vlab-datastore
##ap4414 EDIT: added nfs mount to /etc/fstab
#gusterfs1-dev:volume1 /mnt/vlab-datastore/ nfs async,hard,intr,rw,nolock 0 0

# Read details from Config File
# reading from config file
dbhost=$(awk -F ":" '/VITAL_DB_HOST/ {print $2}' ../../../../config/config.ini | tr -d ' ')
dbpass=$(awk -F ":" '/VITAL_DB_PWD/ {print $2}' ../../../../config/config.ini | tr -d ' ')
dbname=$(awk -F ":" '/VITAL_DB_NAME/ {print $2}' ../../../../config/config.ini | tr -d ' ')
dbuser=$(awk -F ":" '/VITAL_DB_USER/ {print $2}' ../../../../config/config.ini | tr -d ' ')
dbport=$(awk -F ":" '/VITAL_DB_PORT/ {print $2}' ../../../../config/config.ini | tr -d ' ')



# sets up required bridges and bonds for the courses on web server
nets=$(PGPASSWORD=$dbpass psql -U $dbuser -d $dbname -h $dbhost -p $dbport -t -c "SELECT c.id from vital_course c join vital_network_configuration n on c.id=n.course_id where c.status='ACTIVE' and n.is_course_net=True")

set -f
array=(${nets// / })



for var in "${array[@]}"
do
    /home/vital/vital2.0/source/virtual_lab/vital_site/scripts/ws_course_network_startup.sh $var
done
