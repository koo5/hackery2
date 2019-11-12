#!/usr/bin/env python3


import sys
import psycopg2
from collections import defaultdict, namedtuple
import datetime


Rec = namedtuple('Rec', ['action', 'ts', 'desc'])

def make_conn():
	conn = psycopg2.connect("dbname=hours user=hours password=hours")
	return conn

def store(action, misc):
	sql = """INSERT INTO hours(ts,action,misc) VALUES(CURRENT_TIMESTAMP, %s, %s);"""
	with make_conn() as conn:
		with conn.cursor() as curs:
			curs.execute(sql, (action, misc))

def report0():
	sql = """SELECT * FROM hours ORDER BY ts;"""
	with make_conn() as conn:
		with conn.cursor() as curs:
			curs.execute(sql)
			for r in curs.fetchall():
				yield Rec(*r)


def report1():
	runs = []
	on = False
	task = '???'
	last_start = None

	def start(r):
		nonlocal on, last_start
		if not on:
			on = True
			last_start = r.ts

	def stop(r):
		nonlocal on
		if on:
			on = False
			last_run = r.ts - last_start
			if len(runs) and runs[-1][0] == task:
				runs[-1] = (task, runs[-1][1] + [last_run])
			else:
				runs.append((task, [last_run]))

	for r in report0():
		#print (r)
		if r.action == 'on':
			start(r)
		if r.action == 'off':
			stop(r)
		if r.action == 'desc':
			if on:
				stop(r)
				task = r.desc
				start(r)
			else:
				task = r.desc
	#print()
	stop(Rec('off', datetime.datetime.utcnow(), ''))
	return runs

def report2():
	result = []
	for (task,durations) in report1():
		result.append((task, sum(durations, datetime.timedelta())))
	return result







def report3():
	runs = defaultdict(list)

arg = sys.argv[1]
if arg in ['on', 'off', 'desc']:
	misc = ''
	if arg == 'desc':
		misc = sys.argv[1:]
	store(arg, misc)
elif arg == 'dump0':
	for r in records():
		print(r)
elif arg == 'dump1':
	for i in report1():
		print (i)
elif arg == 'dump2':
	for (task,duration) in report2():
		print (str(duration), task)
else:
	raise('unknown command')
