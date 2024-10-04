
count = 0

with open('file', 'w') as f:
	f.write('0')


while True:
	with open('file', 'r') as f:
		r = f.read()
	if r != str(count):
		raise Exception(f'{r} != {count}')
	count += 1
	with open('file', 'w') as f:
		f.write(str(count))

