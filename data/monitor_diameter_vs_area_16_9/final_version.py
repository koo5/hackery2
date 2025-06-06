import sys
from sympy import *

for d in range(1, 100) :
#for d in [6.3] :
#for d in [6.44] :	
#for d in [6.67] :	
#for d in [6.4] :	
	D,W,H,Aimp,Am = symbols('d w h, Aimp, Am', nonnegative=True)
	#r = solve((Eq(D*D, W*W+H*H).subs(D,d), Eq(W/H, 19.5/9),Eq(Aimp,W*H),Eq(Am, Aimp * (2.54**2)/10000)))
	r = solve((Eq(D*D, W*W+H*H).subs(D,d), Eq(W/H, 16/9),Eq(Aimp,W*H),Eq(Am, Aimp * (2.54**2)/10000)))
	#r = solve((Eq(D*D, W*W+H*H).subs(D,d), Eq(W/H, 20/9),Eq(Aimp,W*H),Eq(Am, Aimp * (2.54**2)/10000)))
	rr = r[0]
	Wcm = rr[W] * 2.54
	Hcm = rr[H] * 2.54
	print("""diag:{}″ area:{:.6f}m² w:{:.1f}cm h:{:.1f}cm""".format(d, rr[Am], Wcm, Hcm))
	#print('diag:', d, '" area[m]:', rr[Am], 'W:', Wcm, 'cm H:', Hcm, 'cm')
	
