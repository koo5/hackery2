#!/usr/bin/env fish


sudo swipl -s /home/koom/h/disks.pl  -g "start";
cd /bac16


set l0 (losetup -f)
losetup -P  $l0 ./nvme0n1
set l1 (losetup -f)
losetup -P  $l1 ./nvme1n1

partprobe


cryptsetup luksOpen {$l1}p2 r6 --key-file  /keyfile1


cryptsetup luksOpen {$l0}p6 r6_2 




mount /dev/mapper/r6 /mnt2
