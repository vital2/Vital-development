#!/bin/bash

id=$1

cat >/home/vlab_scp/vmnet_conf/vlab_natdhcp/Nat-$id.dhcpd <<EOL
start           10.$id.1.50
end             10.$id.1.250
interface       bond0.$id
option  subnet  255.255.255.0
opt     router  10.$id.1.1
option  dns     128.238.2.38
option  domain  nyu.edu
option  lease   3600
pidfile /home/vlab_scp/vmnet_conf/run/nat-$id.pid
lease_file /home/vlab_scp/vmnet_conf/leases/nat-$id.leases
EOL