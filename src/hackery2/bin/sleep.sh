#!/usr/bin/env fish
set -x
set DISPLAY :0 
screen_off.sh
sudo rmmod -vvvv aquantia;
sudo rmmod -vvvv atlantic;
sleep 5;
all_usb_wakeup.sh disabled;
sudo bash -c " echo mem > /sys/power/state" ;
sleep 10;
sudo modprobe -vvvv atlantic;
sudo dmesg --follow;



