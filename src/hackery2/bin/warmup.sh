#!/usr/bin/env fish

vlc /SD1 &
psensor &
xbacklight =100 &
sudo terminator  -x fish -c "btrfs scrub start -R -B /mx500data/" &
xfce4-terminal   -x fish -c "startup-firefox.sh" &
sudo terminator -x fish -c "memtester 10G "&
xfce4-terminal  -x fish -c "glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen& glxgears -fullscreen" &
sudo terminator -x fish -c "sha1sum /dev/sd*" &
xfce4-terminal  -x fish -c "sysbench --time 600 --test=cpu --cpu-max-prime=20000 run --threads=24"


