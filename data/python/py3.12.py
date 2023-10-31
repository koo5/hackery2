#type IntOrErrMsg = Expected[int, str]


class Expected[T, Err]:
	def ddd(self):
		print('hhh' + str(T))



a = Expected()
a.ddd()
