#!/bin/bash
sync
lsblk -ndo NAME,ROTA |
awk '$2==1 {print "/dev/"$1}' |
xargs -r sudo hdparm -C
