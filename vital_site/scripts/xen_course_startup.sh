#!/bin/bash

function create_bond {

  for vlan in $*
  do
    vconfig add bond0 $vlan
    #openvswitch command JL
    #ovs-vsctl set port bond0 tag=$vlan
    #JL
    ifconfig bond0.$vlan up
  done

}

function add_bridge_if {

  brdg=$1
  bond=$2

  echo "Creating $bond on $brdg"
  brctl addbr $brdg
  ifconfig $brdg up
  brctl addif $brdg $bond
}

# TODO pick these up database
# creates bonds for courses
create_bond 12 14
# creates bridges for courses
add_bridge_if Net-CS6823 bond0.12
add_bridge_if Net-CS6373 bond0.14