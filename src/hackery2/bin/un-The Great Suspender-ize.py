#!/usr/bin/env python3
import sys
c=0
for l in open(sys.argv[1]):
	c += 1
	start = """chrome-extension://klbibkeccnjlkjkiokjodocebajanakg/suspended.html#ttl="""
	end = "&uri="
	if start in l:
		start_pos = l.find(start)
		l2 = l[:start_pos] + l[l.find(end) + len(end):]
		#print(l)
		print (l2)
		#from IPython import embed; embed()
		continue
	start = """chrome-extension://klbibkeccnjlkjkiokjodocebajanakg/suspended.html#uri="""
	if start in l:
		start_pos = l.find(start)
		l2 = l[:start_pos] + l[start_pos + len(start):]
		#print(l)
		print (l2)
		#from IPython import embed; embed()
		continue
	else:
		print (l)
#print (c)
