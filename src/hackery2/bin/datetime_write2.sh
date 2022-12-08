#!/usr/bin/env bash
#cd /home/koom/snap/obs-studio/current
cd /run/
while :
do
	echo -n "UTC " > datetime2.txt.tmp
	date --utc "+%Y-%m-%d_%H-%M-%S" >> datetime2.txt.tmp
	cat datetime2.txt.tmp > datetime2.txt
	
	cp datetime2.txt /
	cp datetime2.txt /d/
	cp datetime2.txt /bac4/cold/
	cp datetime2.txt /a/images_r6/	
	
	sleep `calc 60*60*24`
	#logger -p user.error xxxx
	#echo '<4>message at log level 4'
done


