#!/bin/sh
for i in $(dpkg -L toilet-fonts|grep -i /usr/share/figlet); do echo $i; toilet -f $(echo $i|sed -e "s#.tlf##g" -e "s#/usr/share/figlet/##g") test; done 
