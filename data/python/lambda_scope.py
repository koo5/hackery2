def x():
	xxx = 0
	results = []
	for x in range(0,2):
		xxx += 1
		y = [xxx]
		results.append(lambda z: y + [z])
	return results


lambdas = x()
print((lambdas[0](0),lambdas[1](0)))


