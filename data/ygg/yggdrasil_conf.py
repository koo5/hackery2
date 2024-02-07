import hjson

local_fn = '/etc/yggdrasil/yggdrasil.conf'

def load_local():
	with open(local_fn) as f:
		return load_fp(f)

def load_fp(f):
	return hjson.load(f)

def save_local(x):
	with open(local_fn, 'w') as f:
		return save_fp(f)

def save_fp(f):
	return hjson.dump(f, x)
