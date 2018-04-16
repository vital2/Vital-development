#!/bin/bash

# this script has been given sudo passwordless previlege in sudoers file

if [ $# -lt 2 ]
then
        echo "Usage: $0 <action> <user_name> <opt:password>";
        exit;
fi

action=$1
user=$2
if [ "$action" == "create" ]; then
  passwd=$3
  ssh vlab-sftp "/s905060/create_user.sh" $user $passwd
elif [ "$action" == "resetpass" ]; then
  passwd=$3
  ssh vlab-sftp "/s905060/mod_user_password.sh" $user $passwd
elif [ "$action" == "remove" ]; then
  ssh vlab-sftp "/s905060/rm_user.sh" $user
fi
