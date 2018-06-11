#!/bin/bash

vlan=$1
vconfig add bond0 $vlan
ifconfig bond0.$vlan 10.$vlan.1.1 netmask 255.255.255.0 broadcast 10.$vlan.1.255 up

# NAT forward requests from xen vms to vital
#iptables -t nat -A POSTROUTING -s 10.$vlan.1.0/24 -o eth0 -j SNAT --to 128.238.77.20
#iptables -A INPUT -i bond0.$vlan -p udp --dport 67:68 --sport 67:68 -j ACCEPT

##ap4414 EDIT: moving NAT forward requests to front of the chain
iptables -t nat -I POSTROUTING 1 -s 10.$vlan.1.0/24 -o eth0 -j SNAT --to 128.238.77.20

iptables -I INPUT 1 -i bond0.$vlan -p udp --dport 67:68 --sport 67:68 -j ACCEPT

##ap4414 EDIT: drop any traffic to Vital web-server
iptables -A INPUT -s 10.$vlan.1.0/24 -j DROP

#Forward all SFTP requests
#iptables -A FORWARD -i bond0.$vlan -s 10.$vlan.1.0/24 -d 128.238.66.35 -p tcp --dport 22 -j ACCEPT
#iptables -A FORWARD -i bond0.$vlan -s 10.$vlan.1.0/24 -d 10.$vlan.1.0/24 -j ACCEPT

##ap4414 EDIT: moving SFTP requests to front of the chain
SERVER_IP="128.238.77.36"
iptables -I FORWARD 1 -i bond0.$vlan -s 10.$vlan.1.0/24 -d $SERVER_IP -p tcp --dport 22 -j ACCEPT

iptables -I FORWARD 2 -i bond0.$vlan -s $SERVER_IP -d 10.$vlan.1.0/24 -j ACCEPT

iptables -I FORWARD 3 -i bond0.$vlan -s 10.$vlan.1.0/24 -d 10.$vlan.1.0/24 -j ACCEPT

requires_internet=$(psql -U postgres -d vital_db -t -c "SELECT n.has_internet_access from vital_course c join vital_network_configuration n on c.id=n.course_id where n.is_course_net=True and c.id="+$vlan)

if [ $requires_internet = 't' ]
then
        echo "Internet enabled for vlan $vlan"
else
        echo "Internet disabled for vlan $vlan"
#       iptables -A FORWARD -i bond0.$vlan -s 10.$vlan.1.0/24 -j REJECT
        iptables -I FORWARD 4 -i bond0.$vlan -s 10.$vlan.1.0/24 -j REJECT
fi
/home/vlab_scp/vmnet_conf/vlab-natdhcp/bin/busybox udhcpd -S /home/vlab_scp/vmnet_conf/vlab-natdhcp/Nat-$vlan.dhcpd
