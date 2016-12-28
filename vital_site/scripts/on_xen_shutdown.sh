# unmount gluster
# reset iptables

#Arjun - edit
umount /mnt/vlab-datastore
echo "Log created from on_xen_shutdown.sh "
echo " Gluster unmounted "

#sudo iptables -F
# Attempting to flush individual iptables rules
iptables -F
echo "Iptables rules flushed"

#Setting NAT tables
iptables -t NAT -A POSTROUTING -s 192.168.122.0/24 -d 224.0.0.0/24 -j RETURN
iptables -t NAT -A POSTROUTING -s 192.168.122.0/24 -d 255.255.255.255/32 -j RETURN
iptables -t NAT -A POSTROUTING -s 192.168.122.0/24 ! -d 192.168.122.0/24 -p tcp -j MASQUERADE --to-ports 1024-65535
iptables -t NAT -A POSTROUTING -s 192.168.122.0/24 ! -d 192.168.122.0/24 -p udp -j MASQUERADE --to-ports 1024-65535
iptables -t NAT -A POSTROUTING -s 192.168.122.0/24 ! -d 192.168.122.0/24 -j MASQUERADE

#setting mangle table
iptables -t MANGLE -A POSTROUTING -o virbr0 -p udp -m udp --dport 68 -j CHECKSUM --checksum-fill

#setting filter table
iptables -t FILTER -A INPUT -i virbr0 -p udp -m udp --dport 53 -j ACCEPT
iptables -t FILTER -A INPUT -i virbr0 -p tcp -m tcp --dport 53 -j ACCEPT
iptables -t FILTER -A INPUT -i virbr0 -p udp -m udp --dport 67 -j ACCEPT
iptables -t FILTER -A INPUT -i virbr0 -p tcp -m tcp --dport 67 -j ACCEPT
iptables -t FILTER -A FORWARD -d 192.168.122.0/24 -o virbr0 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
iptables -t FILTER -A FORWARD -s 192.168.122.0/24 -i virbr0 -j ACCEPT
iptables -t FILTER -A FORWARD -i virbr0 -o virbr0 -j ACCEPT
iptables -t FILTER -A FORWARD -o virbr0 -j REJECT --reject-with icmp-port-unreachable
iptables -t FILTER -A FORWARD -i virbr0 -j REJECT --reject-with icmp-port-unreachable
iptables -t FILTER -A OUTPUT -o virbr0 -p udp -m udp --dport 68 -j ACCEPT
#edit - done
