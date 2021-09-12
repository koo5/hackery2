#!/usr/bin/env python3
import os, time, sys
i = 0
# folder, delay, scrot args
while True:
	os.system("scrot  -q 0  " +sys.argv[3]+ " " +  sys.argv[1]+"/$(date +%Y%m%d%H%M%S).png")
#	os.system('geeqie -r --first')



	# print free space, very smartly

	if i == 0:
		os.system("df -h " + sys.argv[1])
	else:
		os.system("df -h " + sys.argv[1] + " | tail -n 1")
	i += 1
	if i > 10:
		i = 0



	time.sleep(int(sys.argv[2]))

