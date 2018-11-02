#!/usr/bin/env bash

xfwm4 --replace &
~/hackery2/src/hackery2/bin/remap_numrow 
bash -v ~/hackery2/src/hackery2/bin/update-yum 
#sudo mount -t 9p -o trans=virtio,version=9p2000.L shared /shared
ping 8.8.8.8
cat


