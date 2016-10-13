# unmount gluster
# reset iptables

#Arjun - edit
umount /mnt/vlab-datastore
echo "Log created from on_xen_shutdown.sh "
echo " Gluster unmounted "

sudo iptables -F
echo "Iptables rules flushed"

#edit - done
