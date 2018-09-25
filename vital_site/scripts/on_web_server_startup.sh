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
host=$(awk -F ":" '/VITAL_DB_HOST/ {print $2}' /home/vital/config.ini | tr -d ' ')
pass=$(awk -F ":" '/VITAL_DB_PWD/ {print $2}' /home/vital/config.ini | tr -d ' ')
sftp=$(awk -F ":" '/SFTP_ADDR/ {print $2}' /home/vital/config.ini | tr -d ' ')
localrepo=$(awk -F ":" '/LOCAL_REPO/ {print $2}' /home/vital/config.ini | tr -d ' ')

# sets up required bridges and bonds for the courses on web server
nets=$(PGPASSWORD=$pass psql -U postgres -d vital_db -h $host -t -c "SELECT c.id from vital_course c join vital_network_configuration n on c.id=n.course_id where c.status='ACTIVE' and n.is_course_net=True")
set -f
array=(${nets// / })

# Flush Iptables
iptables -F

for var in "${array[@]}"
do
    /home/vital/vital2.0/source/virtual_lab/vital_site/scripts/ws_course_network_startup.sh $var
done

# enables SFTP access to the SFTP server and local ubuntu repo from xen vms
# TODO change the hardcorded server IP
SERVER_IP=( $sftp $localrepo )

for ip in "${SERVER_IP[@]}"
do
    iptables -I FORWARD 2 -p icmp --icmp-type 8 -s 0/0 -d $ip -m state --state NEW,ESTABLISHED,RELATED -j ACCEPT
    iptables -I FORWARD 1 -p icmp --icmp-type 0 -s $ip -d 0/0 -m state --state ESTABLISHED,RELATED -j ACCEPT
done

# to enable NAT from xen
#iptables -t nat -A POSTROUTING -s 192.168.35.0/24 -o eth0 -j MASQUERADE
##ap4414 EDIT: moving iptables rules to the front of the chain
iptables -t nat -I POSTROUTING 1 -s 192.168.35.0/24 -o eth0 -j MASQUERADE
