#!/usr/bin/env fish


ping -c 20 8.8.8.8; or sudo dhclient -v enp0s25

cat /sys/class/net/enp0s25/carrier | grep 1; and begin

	sudo dhcping -s  192.168.8.1   -h "a4:5d:36:9b:18:16"; and begin
		sudo nmcli c show 'strasnice drat!' | grep GENERAL.STATE: | grep activated; 
		and exit 0;
		sudo nmcli c up 'strasnice drat!';
		and sudo nmcli c down 'Not Mi Phone';
		and exit 0;
	end;

	sudo dhcping -s  10.0.0.138    -h "a4:5d:36:9b:18:16"; and begin
		sudo nmcli c show 'prosek drat'         | grep GENERAL.STATE: | grep activated; 
		and exit 0;
		sudo nmcli c up 'prosek drat';
		and sudo nmcli c down 'Not Mi Phone';
		and exit 0;
	end;

exit 0


#	sudo nmcli c show 'xWLAN1-5G-FA4J68' | grep GENERAL.STATE: | grep activated;
#	and exit 0;
#	sudo nmcli c show 'xWLAN1-FA4J68' | grep GENERAL.STATE: | grep activated;
#	and exit 0;
