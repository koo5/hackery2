#!/usr/bin/env bash
#sudo systemctl restart spice-vdagent
#sudo spice-vdagent -x -d
#xfwm4 --replace &
~/hackery2/src/hackery2/bin/remap_numrow 
sudo ~/hackery2/src/hackery2/bin/update-yum
ret_code=$?
#sudo mount -t 9p -o trans=virtio,version=9p2000.L shared /shared
exit $ret_code


