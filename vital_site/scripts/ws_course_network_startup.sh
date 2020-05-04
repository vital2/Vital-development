#!/bin/bash

#reading from config file
host=$(awk -F ":" '/VITAL_DB_HOST/ {print $2}' ../../../../config/config.ini | tr -d ' ')
pass=$(awk -F ":" '/VITAL_DB_PWD/ {print $2}' ../../../../config/config.ini | tr -d ' ')
port=$(awk -F ":" '/VITAL_DB_PORT/ {print $2}' ../../../../config/config.ini | tr -d ' ')
dbname=$(awk -F ":" '/VITAL_DB_NAME/ {print $2}' ../../../../config/config.ini | tr -d ' ')

vlan=$1
if /sbin/ethtool bond0.$vlan | grep -q "Link detected: yes"; then
    echo "Online"
else
    echo "Not online"
    vconfig add bond0 $vlan
    ifconfig bond0.$vlan 10.$vlan.1.1 netmask 255.255.255.0 broadcast 10.$vlan.1.255 up
fi

requires_internet=$(PGPASSWORD=$pass psql -U postgres -d $dbname -h $host -p $port -t -c "SELECT n.has_internet_access from vital_course c join vital_network_configuration n on c.id=n.course_id where n.is_course_net=True and c.id="+$vlan)

iptables -C FORWARD -i bond0.$vlan -s 10.$vlan.1.0/24 -j REJECT

if  [ $(echo $?) == '1' ] && [ $requires_internet = 'f' ]
then
	 echo "Rule Added"
        iptables -I FORWARD 2 -i bond0.$vlan -s 10.$vlan.1.0/24 -j REJECT
else
        echo "No need to add the rule"
fi

/home/vlab_scp/vmnet_conf/vlab-natdhcp/bin/busybox udhcpd -S /home/vlab_scp/vmnet_conf/vlab-natdhcp/Nat-$vlan.dhcpd
