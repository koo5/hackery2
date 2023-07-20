#!/usr/bin/env fish
set -x
set DISPLAY :0 
#screen_off.sh

sudo chvt 2; sudo bash -c " echo mem > /sys/power/state" ;

sudo systemctl disable --now lightdm &
sleep 2;
sudo rmmod -f nvidia_drm nvidia_modeset nvidia_uvm &

sudo rmmod -vvvv aquantia;
sudo rmmod -vvvv atlantic;
sleep 5;
all_usb_wakeup.sh disabled;





sleep 5;
sudo modprobe -vvvv atlantic;

sudo modprobe nvidia_drm nvidia_modeset nvidia_uvm;
sudo systemctl enable --now lightdm;

sudo dmesg --follow;



