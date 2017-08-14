#!/usr/bin/env python3
import os, time, sys
print (sys.argv)
sleep_time = int(sys.argv[1])
snapshotted_dir = sys.argv[2]
snapshots_dir = sys.argv[3]
os.system("sudo which python3")
while True:
	os.system("sudo " + os.path.dirname(os.path.abspath(__file__)) + "/" + "prune_snaps.py " + snapshots_dir)
	os.system("sudo " + os.path.dirname(os.path.abspath(__file__)) + "/" + "snap.fish " + snapshotted_dir + " " + snapshots_dir)
	time.sleep(sleep_time)
