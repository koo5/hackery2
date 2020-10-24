#!/usr/bin/env python
# -*- coding: utf8 -*-

from random import randrange, choice
from time import sleep, asctime

#while True:
#	print '\t' * randrange(12), '\033[93m' , asctime()
#	sleep(0.1)

from termcolor import colored

#print colored('hello', 'red'), colored('world', 'green')

#now let's randomize the color

colorsl = ['grey', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']
c = 0
while True:
    c += 1
    print '\t' * randrange(16), colored('λ', choice(colorsl)) if randrange(2) == 0 or c < 20  else colored("`", choice(colorsl))
    
    sleep(0.1)
