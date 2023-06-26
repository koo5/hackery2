#!/usr/bin/env python3


import os,time,datetime,subprocess,shlex,glob,pathlib,json,sys
j = json.load(open(sys.argv[1]))
for macro in j['macros']:
	for condition in macro['conditions']:
		if condition["id"] == "cursor":
			for key in ['maxX','minX']:
				condition[key] += int(sys.argv[2])
			for key in ['maxY','minY']:
				condition[key] += int(sys.argv[3])
print(json.dumps(j,indent=4))
