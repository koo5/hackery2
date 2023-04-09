#!/usr/bin/env bash
#sudo systemctl restart spice-vdagent
#sudo spice-vdagent -x -d
#xfwm4 --replace &

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
bash "$DIR/remap_numrow"
bash "$DIR/noblank.sh"

#ret_code=$?
#sudo mount -t 9p -o trans=virtio,version=9p2000.L shared /shared
#exit $ret_code



