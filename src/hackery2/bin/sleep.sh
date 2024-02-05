#!/usr/bin/env fish
set -x
sudo umount -f /home/koom/snap/firefox/common/.mozilla/firefox/hpp
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



