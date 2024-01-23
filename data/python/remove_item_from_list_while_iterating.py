import random

li = list(range(10))
random.shuffle(li)

print(f'{li=}')
for x in li:#reversed(li):
	print(f'see {x}')
	if x < 5:
		li.remove(x)
			
print(f'{li=}')


