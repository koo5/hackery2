#!/bin/env bash
cd /run/user/1000
while :
do
	echo -n "UTC " > datetime.txt.tmp
	date --utc "+%Y-%m-%d_%H-%M-%S" >> datetime.txt.tmp
	cat datetime.txt.tmp > datetime.txt
	sleep 1
done


