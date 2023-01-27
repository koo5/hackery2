#!/usr/bin/env fish
for i in /sys/bus/usb/devices/*/power/wakeup; 
	echo -n "$i "; 
	cat $i | tr '\n' ' ';
	echo -n  "-> ";
	echo $argv[1];
	sudo bash -c "echo $argv[1] > $i"; 
end
