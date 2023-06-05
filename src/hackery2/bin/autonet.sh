#!/usr/bin/env fish

ping 8.8.8.8 -c 1; and exit 0

sudo dhclient -v enp0s25

sudo dhcping -s    192.168.8.1   -h "a4:5d:36:9b:18:16";   and sudo nmcli c up 'strasnice drat!'
sudo dhcping -s    10.0.0.138    -h "a4:5d:36:9b:18:16";   and sudo nmcli c up 'prosek drat'




exit 0
