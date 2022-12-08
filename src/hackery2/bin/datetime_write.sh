#!/usr/bin/env bash
#cd /home/koom/snap/obs-studio/current
cd /run/
while :
do
	#echo -n "UTC " > datetime.txt.tmp
	date --utc "+%Y-%m-%dT%H-%M-%SZ" > datetime.txt.tmp
	cat datetime.txt.tmp > datetime.txt
	sleep 1
	#logger -p user.error xxxx
	#echo '<4>message at log level 4'
done


