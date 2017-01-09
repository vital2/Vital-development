#!/bin/bash

if [ $# -eq 0 ]
then
        echo "Usage: $0 <vlan> +internet"
        exit
fi

vlan=$1
vconfig add bond0 $vlan
ifconfig bond0.$vlan 10.$vlan.1.1 netmask 255.255.255.0 broadcast 10.$vlan.1.255 up

# NAT forward requests from xen vms to vital
iptables -t nat -A POSTROUTING -s 10.$vlan.1.0/24 -o eth0 -j SNAT --to 128.238.77.20

iptables -A INPUT -i bond0.$vlan -p udp --dport 67:68 --sport 67:68 -j ACCEPT

#Forward all SFTP requests
iptables -A FORWARD -i bond0.$vlan -s 10.$vlan.1.0/24 -d 128.238.66.35 -p tcp --dport 22 -j ACCEPT

iptables -A FORWARD -i bond0.$vlan -s 10.$vlan.1.0/24 -d 10.$vlan.1.0/24 -j ACCEPT

if [ $# -eq 2 ] && [ "$2" = '+internet' ]
then
        echo "Internet enabled for vlan $vlan"
else
        iptables -A FORWARD -i bond0.$vlan -s 10.$vlan.1.0/24 -j REJECT
fi
/home/vlab_scp/vmnet_conf/vlab-natdhcp/bin/busybox udhcpd -S /home/vlab_scp/vmnet_conf/vlab-natdhcp/Nat-$vlan.dhcpd
