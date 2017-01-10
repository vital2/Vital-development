#!/bin/bash

# This is called from upstart job /etc/init/on_server_start.conf
# postgres init script modified for this. similar to http://blog.systemed.net/post/6

# mounts glusterfs
mount -t glusterfs gusterfs1-dev:volume1 /mnt/vlab-datastore

# sets up required bridges and bonds for the courses on web server
nets=$(psql -U postgres -d vital_db -t -c "SELECT c.id from vital_course c join vital_network_configuration n on c.id=n.course_id where c.status='ACTIVE'")
set -f
array=(${nets// / })

for var in "${array[@]}"
do
    /home/rdj259/vital2.0/source/virtual_lab/vital_site/scripts/ws_course_network_startup.sh $var
done

# enables SFTP access to the SFTP server from xen vms
# TODO change the hardcorded server IP
SERVER_IP="128.238.66.35"
iptables -I FORWARD 1 -p icmp --icmp-type 8 -s 0/0 -d $SERVER_IP -m state --state NEW,ESTABLISHED,RELATED -j ACCEPT
iptables -I FORWARD 1 -p icmp --icmp-type 0 -s $SERVER_IP -d 0/0 -m state --state ESTABLISHED,RELATED -j ACCEPT

# to enable NAT from xen
iptables -t nat -A POSTROUTING -s 192.168.35.0/24 -o eth0 -j MASQUERADE
