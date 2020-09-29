import time

def aaa():
#	while True:
		print "cyklus aaa"
		for i in array:
			yield i


array = ['a','b','c','d','e']


X = 0
for j in aaa():
	print j
	X = X + 1
	array.append( X)
	time.sleep(0.1)


#for i in array:
#	print i
#	del array[:]
	
	