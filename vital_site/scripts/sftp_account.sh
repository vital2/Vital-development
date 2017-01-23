#!/bin/sh

# this script has been given sudo passwordless previlege in sudoers file

while getopts a:u:x: opt
do
    case "$opt" in
        a) action=$OPTARG;;
        u) user=$OPTARG;;
        x) passwd=$OPTARG;;
        \?) echo "Usage [action user password]"; exit 1;; #Invalid argument
    esac
done
echo $action
echo $user

if [ "$action" == "create" ]; then
  echo $passwd
  ssh 128.238.66.35 "/root/bin/create_user.sh" -u $user -x $passwd
elif [ "$action" == "resetpass" ]; then
  echo $passwd
  ssh 128.238.66.35 "/root/bin/mod_user_password.sh" -u $user -x $passwd
elif [ "$action" == "remove" ]; then
  ssh 128.238.66.35 "/root/bin/rm_user.sh" -u $user
fi
