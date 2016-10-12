#!/bin/bash

# TODO Needs to be changed for specific student


if [ $# -ne 2 ]
then
   echo "USAGE: $0  <start student id> <stop student id>"
   exit;
fi


echo -- $1 $2
let sindex=$1
let eindex=$2


for ((i=sindex; i <= eindex; i++))
do

    let net_id=$i
    net_name="Net-${net_id}"
    echo "creating ${net_name} on ${xen_server}"
    brctl addbr ${net_name}
    #openvswitch command JL
    #ovs-vsctl add-br ${net_name}
    #JL
    ifconfig ${net_name} up

   second_net_id=$((${net_id} + 2000))
   second_net_name="Net-${second_net_id}"
   echo "creating ${second_net_name} on ${xen_server}"
   #openvswitch command JL
   #ovs-vsctl add-br ${second_net_name}
   brctl addbr ${second_net_name}
   ifconfig ${second_net_name} up

done