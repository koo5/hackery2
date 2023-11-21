import datetime

def generate_unique_filename():
	return str(datetime.datetime.utcnow()).replace(' ', '_').replace(':', '_')
