#!/bin/bash
if [ $# -eq 0 ]
then
        echo "Usage: $0 <vlan>"
        exit
fi

vlan=$1

iptables -t nat -D POSTROUTING -s 10.$vlan.1.0/24 -o eth0 -j SNAT --to 128.238.77.20
iptables -D INPUT -i bond0.$vlan -p udp --dport 67:68 --sport 67:68 -j ACCEPT
iptables -D FORWARD -i bond0.$vlan -s 10.$vlan.1.0/24 -d 128.238.66.35 -p tcp --dport 22 -j ACCEPT
iptables -D FORWARD -i bond0.$vlan -s 10.$vlan.1.0/24 -d 10.$vlan.1.0/24 -j ACCEPT
iptables -D FORWARD -i bond0.$vlan -s 10.$vlan.1.0/24 -j REJECT

kill `cat /home/vlab_scp/vmnet_conf/run/nat-$vlan.pid`
ifconfig bond0.$vlan down
vconfig rem bond0.$vlan