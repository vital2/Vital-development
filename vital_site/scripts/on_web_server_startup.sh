#!/bin/bash

# mounts glusterfs
mount -t glusterfs gusterfs1-dev:volume1 /mnt/vlab-datastore

# sets up required bridges and bonds for the courses on web server
# TODO Needs to be populated automatically from database
# TODO Find a better location for nat-start script
# TODO replace with course_startup script

#Arjun - edit
for var in "$@"
do
    /home/vlab_scp/vmnet_conf/vlab-natdhcp/nat-start.sh var
done
#edit - done

#/home/vlab_scp/vmnet_conf/vlab-natdhcp/nat-start.sh 12
#/home/vlab_scp/vmnet_conf/vlab-natdhcp/nat-start.sh 14

# enables SFTP access to the SFTP server from xen vms
# TODO change the hardcorded server IP

SERVER_IP="128.238.66.35"
iptables -I FORWARD 1 -p icmp --icmp-type 8 -s 0/0 -d $SERVER_IP -m state --state NEW,ESTABLISHED,RELATED -j ACCEPT
iptables -I FORWARD 1 -p icmp --icmp-type 0 -s $SERVER_IP -d 0/0 -m state --state ESTABLISHED,RELATED -j ACCEPT

# to enable NAT from xen
iptables -t nat -A POSTROUTING -s 192.168.35.0/24 -o eth0 -j MASQUERADE
