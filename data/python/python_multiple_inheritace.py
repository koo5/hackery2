class base1c():
	def x(s, d):
		print("base1->")
		print("<-base1")
class base2n():
	def x(s, c1, c2, c3, c4):
		print("base2->")
		#super().x()
		print("<-base2")
class main (base2n, base1c):
	def x(s):
		print("main->")
		base2n.x(s,1,2,3,4)
		base1c.x(s,55)
		print("<-main")

main().x()