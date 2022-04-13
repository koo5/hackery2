#!/usr/bin/env bash

sudo apt update

sudo apt remove '^libreoffice.*'

sudo apt install -y \
   arandr autorandr btrfs-progs build-essential duperemove fdupes firewall-config fish fslint geany git gparted hddtemp hdparm htop iotop jnettop libxrandr-dev lsof mailcheck mc powertop python3 screen smartmontools spectre-meltdown-checker ssh swi-prolog tcpdump terminator tmux traceroute virt-manager wget xcalib zram-config

# sudo apt install kde-plasma-desktop
# sudo apt install xubuntu-desktop
# sudo apt install xfce-desktop


