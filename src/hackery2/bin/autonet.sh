#!/usr/bin/env fish

#ping 8.8.8.8 -c 1; and exit 0

sudo nmcli c show 'strasnice drat!' | grep GENERAL.STATE: | grep activated; and exit 0;
sudo nmcli c show 'prosek drat'     | grep GENERAL.STATE: | grep activated; and exit 0;

sudo dhclient -v enp0s25

sudo dhcping -s  192.168.8.1   -h "a4:5d:36:9b:18:16";   and sudo nmcli c up 'strasnice drat!'; and sudo nmcli c down 'Not Mi Phone'
sudo dhcping -s  10.0.0.138    -h "a4:5d:36:9b:18:16";   and sudo nmcli c up 'prosek drat'; and sudo nmcli c down 'Not Mi Phone'

exit 0
