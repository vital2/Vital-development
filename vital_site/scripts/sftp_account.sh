#!/bin/bash

if [ $# -lt 2 ]
then
        echo "Usage: $0 <action> <user_name> <opt:password>";
        exit;
fi

action=$1
user=$2
if [ "$action" == "create" ]; then
  passwd=$3
  ssh 128.238.66.35 "/usr/home/s905060/create_user.sh $user $passwd"
fi

# else to remove account - TODO