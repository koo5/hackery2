#!/bin/bash
TMPVAR=`systemctl status sddm.service`
echo "TMPVAR = $TMPVAR"
TMPVAR2=$(echo $TMPVAR | cut -d '{' -f 2)
echo "TMPVAR2 = $TMPVAR2"
TMPVAR3=$(echo $TMPVAR2 | cut -d '}' -f 1)
echo "TMPVAR3 = $TMPVAR3"
TMPVAR4="/var/run/sddm/\{$TMPVAR3\}"
echo "TMPVAR4 = $TMPVAR4"
echo "starting VNC server with string: sudo x11vnc -auth $TMPVAR4 -
nopw -ncache 10"
x11vnc -auth $TMPVAR4 -nopw
