#!/usr/bin/env fish

sudo swipl -s /home/koom/h/disks.pl  -g "start"


export DST=bac1

mount | grep $DST ; and backup_cold.sh
mount | grep $DST ; and backup_lean.sh
mount | grep $DST ; and backup_root.sh

export DST=bac3

mount | grep $DST ; and backup_lean.sh
mount | grep $DST ; and backup_root.sh

export DST=bac4

mount | grep $DST ; and backup_lean.sh
mount | grep $DST ; and backup_root.sh

export DST=bac8

mount | grep $DST ; and backup_cold.sh
mount | grep $DST ; and backup_lean.sh
mount | grep $DST ; and backup_root.sh

export DST=bac9

mount | grep $DST ; and backup_cold.sh



#sudo swipl -s /home/koom/h/disks.pl  -g "stop"
