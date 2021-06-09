
import sys


def float_range(start, stop, step):
	while start < stop:
		yield float(start)
		start += step
    
for i in list(float_range(2.8,5.0,0.1)): 
	sys.stdout.write("%.2f," % i) 
