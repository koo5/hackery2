#!/usr/bin/env python
# -*- coding: utf8 -*-
import sys
print """
  _      ______ __  __  ____  _   _ 
 | |    |  ____|  \/  |/ __ \| \ | |
 | |    | |__  | \  / | |  | |  \| |
 | |    |  __| | |\/| | |  | | . ` |
 | |____| |____| |  | | |__| | |\  |
 |______|______|_|  |_|\____/|_| \_| Shell v0.1
                                    
                                    """

prompt = "lemon> "

def getSentenceInfo(sentence):
	"""Sorry python, i had to use camelcase"""
	pass

try:
	while True:
		inp = raw_input(prompt)
		lnp = inp.split()
		#print inp, lnp
		if lnp[0] == 'echo' or 'say':
			print ' '.join(lnp[1:])
		elif lnp[0] == 'exit' or 'quit':
			print "Bye!"
			sys.exit(0)
		
except KeyboardIntbvcderrupt:
	print "Exit by typing `exit'"
