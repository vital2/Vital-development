#!/bin/bash
  
# reading from config file
host=$(awk -F ":" '/VITAL_DB_HOST/ {print $2}' /home/vital/config.ini | tr -d ' ')
pass=$(awk -F ":" '/VITAL_DB_PWD/ {print $2}' /home/vital/config.ini | tr -d ' ')
port=$(awk -F ":" '/VITAL_DB_PORT/ {print $2}' /home/vital/config.ini | tr -d ' ')


vlan=$1 
if /sbin/ethtool eth0 | grep -q "Link detected: yes"; then
    echo "Online already"
else
    echo "Not online"
    vconfig add bond0 $vlan
    ifconfig bond0.$vlan 10.$vlan.1.1 netmask 255.255.255.0 broadcast 10.$vlan.1.255 up

fi 
requires_internet=$(PGPASSWORD=$pass psql -U postgres -d vital_dev2 -h $host -p $port -t -c "SELECT n.has_internet_access from vital_course c join vital_network_configuration n on c.id=n.course_id where n.is_course_net=True and c.id="+$vlan)

#EDIT: sg5559
#if requires_internet access is true do nothing
#if requires_internet is false, add a rule to drop the traffic in forward table
#Since requires_internet term is confusing for loop; introducing new term add_rule with boolean value

if [ $requires_internet = "f" ]; then
        add_rule=true
else
        add_rule=false
fi


iptables -C FORWARD -i bond0.$vlan -s 10.$vlan.1.0/24 -j REJECT

out="$(echo $?)"
#EDIT:sg5559
#if rule already exists, skip adding another same rule $(echo $?)
#if block_internet is false, skip adding the rule
#Either of the cases, rule should not be added
#With internet the git access also gets blocked as by default the git request is sent to FORWARD table.

if [ $out = '1' ] && [ $add_rule = 'true' ] ; then 
	echo "Rule does not exists and you need to add a rule to block the internet"
	iptables -I FORWARD 2 -i bond0.$vlan -s 10.$vlan.1.0/24 -j REJECT
else
	echo "Either rule already exists or there is no need to add rule to block the internet"
fi

/home/vlab_scp/vmnet_conf/vlab-natdhcp/bin/busybox udhcpd -S /home/vlab_scp/vmnet_conf/vlab-natdhcp/Nat-$vlan.dhcpd
