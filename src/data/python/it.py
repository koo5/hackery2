
class Triterator:
	def __init__(self, iterable):
		self.iterator = iter(iterable)
		self.items = []
	def next(self):
		self.items.append(next(self.iterator)

class Triteration:
	def __init__(self, triterator, index):
		self.triterator = triterator
		self.index = index

def triterator(x, y):
	triterator = Triterator(x)
	y2 = Triteration(triterator, 0)
	for i in unify(y, y2):
		yield

def first(x, item):
	if not isinstance(x, Triteration):
		return
	if x.index >= len(x.triterator.items):
		x.triterator.next()
	for i in unify(item, x.triterator.items[x.index])
		yield

def rest(x, triteration):
	if not isinstance(x, Triteration):
		return
	list(first(x, None))
	new_triteration = Triteration(x.triterator, x.index + 1)
	for i in unify(triteration, new_triteration)
		yield



