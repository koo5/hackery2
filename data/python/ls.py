#!/usr/bin/env python
import os, sys

cmd = "ls " + sys.argv[1]  + " -Q"
#todo:what if user used -Q, or one of the other quoting formats? can we deal with that? im sure we can!
#cmd = "ls  -a -R" + " -Q"
diredcmd = cmd + " -l --dired"
print cmd

rawdired = os.popen(diredcmd).read()
rawls = os.popen(cmd).read()
dired = rawdired.splitlines()
#print dired

assert dired[-1].startswith("//DIRED-OPTIONS//")

if dired[-2].startswith("//SUBDIRED//"):
	diredline = dired[-3]
	subdired = dired[-2]
else:
	diredline = dired[-2]
	subdired = None
	assert diredline.startswith("//DIRED//")

#print diredline
nums = diredline.split()[1:]
#print nums
assert len(nums)%2 == 0

from itertools import islice, izip
pairs = zip(nums[::2], nums[1::2], ['dunno']*(len(nums)/2))

if subdired != None:
	subnums = subdired.split()[1:]
#	print subnums
	subpairs = zip(subnums[::2], subnums[1::2], ['subdir']*(len(subnums)/2))
	pairs += subpairs
#print pairs

pairs = [(int(p[0]), int(p[1]), p[2]) for p in pairs]
pairs = sorted(pairs, key=lambda x: x[0])

#print "pairs:",pairs

files = []
dirs = []

#print len(list(pairs))

print  "orig------------------------------------------"
print rawls
print  "orig------------------------------------------"


for pair in pairs:
	start,end,kind = pair
	f = rawdired[start:end]
	line = rawdired[:start].rsplit("\n",1)[-1]
	#print pair
	if kind == 'subdir':
		kind = 'dir'
	else:
		if line.startswith("  d"):
			kind = 'dir'
		elif line.startswith("  -"):
			kind = 'file'
		else:
			raise Exception("line is "+repr(line), pair)
	#if we want to handle files with newlines in names, we might try playing with the escaping parameters or be careful about quotes?
	#entries in the subdired list are always dirs
	#print ">>>",f
	files.append((f, kind))

output = ""
start = 0
for f,kind in files:
	pos = rawls.find(f)
	#print pos
	marked =  "<<"+kind+">>"+f+"<</"+kind+">>"
	output += rawls[start:pos] + marked
	tocut = pos+len(f)
	#start = pos + len(f)
	rawls = rawls[tocut:]
print output


