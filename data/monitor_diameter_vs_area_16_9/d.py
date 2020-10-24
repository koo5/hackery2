from math import *
def a(x):
	y = x/16*9
	d = sqrt((16**2*x**2 + 9**2*x**2)/16**2)
	print ("d:%s\t%s\t,a:%s\t,x:%s\t,y:%s\t"%(d/2.54,d,x*y,x,y))

for i in range(20, 212):
	a(i)


