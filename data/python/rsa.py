# https://mi21.vsb.cz/sites/mi21.vsb.cz/files/unit/rsa_sifrovani.pdf
# https://math.fel.cvut.cz/en/people/gollova/mkr/mkr3.pdf
# https://sifrovani.fd.cvut.cz/rsa.html


def gen_primes():
	"""Generate an infinite sequence of prime numbers."""
	D = {}
	q = 2
	while True:
		if q not in D:
			D[q * q] = [q]
			yield q
		else:
			for p in D[q]:
				D.setdefault(p + q, []).append(p)
			del D[q]
		q += 1



def gen_primes_forever_test():
	for p in gen_primes():
		#if p > 100:
		#	break
		print(p)


def gen_key(p,q):
	n = p * q
	phi = (p - 1) * (q - 1)
	e = 1223456
	assert 1 < e < phi
	d = int((e - 1) % phi)
	#print(f'{d:d}')
	k = dict(priv=dict(n=n, d=d), pub=dict(n=n, e=e))
	print(k)
	return k


def encrypt(msg, key):
	n = key['pub']['n']
	e = key['pub']['e']
	
	enc = pow(msg, e, n)
	return enc
	

def print_key(key):
	match key:
		case {'priv':priv, 'pub':pub}:
			pass
	
	assert priv['n'] == pub['n']
	n = priv['n']
	
	print('n = ' + big_number_string(n))
	print('e = ' + big_number_string(pub['e']))
	print('d = ' + big_number_string(priv['d']))
	

def big_number_string(x):
	"""avoid scientific notation"""
	xxx = f'{x:d}'
	return xxx
	


def string_to_int(s):
	return int.from_bytes(s.encode(), byteorder='little')


def int_to_string(i):
    length = math.ceil(i.bit_length() / 8)
    return i.to_bytes(length, byteorder='little').decode()
    

def test():
	p = 113709853
	q = 113711993
	key = gen_key(p, q)
	
	#print_key(key)
	
	#print(key)
	msg = 'Hello, World!'
	print(f'{msg=}')
	msg = string_to_int(msg)
	print(f'{msg=}')
	enc = encrypt(msg, key)
	print(f'{enc=}')
	

test()