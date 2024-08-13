#!/usr/bin/python3

import time, json, os, sys


while True:
	time.sleep(60*15)
	try:
		j = json.loads(os.path.expanduser('~/agent_db.json')
	except Exception as e:
		print(e)
		continue
	host_sleep_state: bool = j.get('host_sleep_state', False)
	
	if host_sleep_state:
		os.system('sleep.sh')
	