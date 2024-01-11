import os
import sys

def secret(name, default=None):

	v = os.environ.get(name)
	if v is not None:
		return v
	
	SECRETS_DIR = os.environ.get('SECRETS_DIR')
	if SECRETS_DIR is None:
		SECRETS_DIR = '/run/secrets'
		if not os.path.isdir(SECRETS_DIR):
			SECRETS_DIR = './secrets'
			if not os.path.isdir(SECRETS_DIR):
				print(f"Error: secret directory too secret.")
				print(f"Hint: SECRETS_DIR=... {sys.argv[0]} ... ?")
				
	fn = SECRETS_DIR + '/' + name
	
	try:
		with open(fn, 'r') as x:
			return x.read()
	except FileNotFoundError:
		if default is not None:
			return default
		else:				
			raise

