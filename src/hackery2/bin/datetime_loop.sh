#!/usr/bin/env bash
#cd /home/koom/snap/obs-studio/current
cd /tmp/
while :
do
	#echo -n "UTC " > datetime.txt.tmp
	#date --utc "+%Y-%m-%dT%H-%M-%S Z" > datetime.txt.tmp
	date "+%Y-%m-%d T %H-%M-%S" > datetime.txt.tmp
	cat datetime.txt.tmp > datetime.txt
	sleep 0.1
	#logger -p user.error xxxx
	#echo '<4>message at log level 4'
done


