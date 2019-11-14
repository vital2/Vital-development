#!/bin/bash

# reading from config file
host=$(awk -F ":" '/VITAL_DB_HOST/ {print $2}' /home/vital/config.ini | tr -d ' ')
pass=$(awk -F ":" '/VITAL_DB_PWD/ {print $2}' /home/vital/config.ini | tr -d ' ')
sftp=$(awk -F ":" '/SFTP_ADDR/ {print $2}' /home/vital/config.ini | tr -d ' ')
localrepo=$(awk -F ":" '/LOCAL_REPO/ {print $2}' /home/vital/config.ini | tr -d ' ')
port=$(awk -F ":" '/VITAL_DB_PORT/ {print $2}' /home/vital/config.ini | tr -d ' ')

vlan=$1
vconfig add bond0 $vlan
ifconfig bond0.$vlan 10.$vlan.1.1 netmask 255.255.255.0 broadcast 10.$vlan.1.255 up

# NAT forward requests from xen vms to vital
#iptables -t nat -A POSTROUTING -s 10.$vlan.1.0/24 -o eth0 -j SNAT --to 128.238.77.20
#iptables -A INPUT -i bond0.$vlan -p udp --dport 67:68 --sport 67:68 -j ACCEPT

##as11552 : EDIT : Add rules to allow DNS requests from Student VM's
iptables -A INPUT -s 10.$vlan.1.0/24 -p udp -m udp --dport 53 -j ACCEPT
iptables -A OUTPUT -d 10.$vlan.1.0/24 -p udp -m udp --sport 53 -j ACCEPT

##ap4414 EDIT: moving NAT forward requests to front of the chain
iptables -t nat -I POSTROUTING 1 -s 10.$vlan.1.0/24 -o enp5s0 -j SNAT --to 128.238.77.21
iptables -I INPUT 1 -i bond0.$vlan -p udp --dport 67:68 --sport 67:68 -j ACCEPT

##ap4414 EDIT: drop any traffic to Vital web-server
iptables -A INPUT -s 10.$vlan.1.0/24 -j DROP

#Forward all SFTP requests
#iptables -A FORWARD -i bond0.$vlan -s 10.$vlan.1.0/24 -d 128.238.66.35 -p tcp --dport 22 -j ACCEPT
#iptables -A FORWARD -i bond0.$vlan -s 10.$vlan.1.0/24 -d 10.$vlan.1.0/24 -j ACCEPT

##ap4414 EDIT: moving SFTP requests to front of the chain
SERVER_IP=$sftp
iptables -I FORWARD 1 -i bond0.$vlan -s 10.$vlan.1.0/24 -d $SERVER_IP -p tcp --dport 22 -j ACCEPT
iptables -I FORWARD 2 -i bond0.$vlan -s $SERVER_IP -d 10.$vlan.1.0/24 -j ACCEPT

##as11552  EDIT: Add rules for accessing Local Repository
SERVER_IP=$localrepo
iptables -I FORWARD 3 -i bond0.$vlan -s 10.$vlan.1.0/24 -d $SERVER_IP -p tcp --dport 80 -j ACCEPT
iptables -I FORWARD 4 -i bond0.$vlan -s $SERVER_IP -d 10.$vlan.1.0/24 -j ACCEPT

iptables -I FORWARD 5 -i bond0.$vlan -s 10.$vlan.1.0/24 -d 10.$vlan.1.0/24 -j ACCEPT

requires_internet=$(PGPASSWORD=$pass psql -U postgres -d vital_db -h $host -p $port -t -c "SELECT n.has_internet_access from vital_course c join vital_network_configuration n on c.id=n.course_id where n.is_course_net=True and c.id="+$vlan)

if [ $requires_internet = 't' ]
then
        echo "Internet enabled for vlan $vlan"
else
        echo "Internet disabled for vlan $vlan"
#       iptables -A FORWARD -i bond0.$vlan -s 10.$vlan.1.0/24 -j REJECT
        iptables -I FORWARD 6 -i bond0.$vlan -s 10.$vlan.1.0/24 -j REJECT
fi
/home/vlab_scp/vmnet_conf/vlab-natdhcp/bin/busybox udhcpd -S /home/vlab_scp/vmnet_conf/vlab-natdhcp/Nat-$vlan.dhcpd
