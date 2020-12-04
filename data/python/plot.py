#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from snoop import snoop

import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('GTK3Cairo')

n = 100000

@snoop
def x():
    for i in range(1,n):
        hide =  i % (1+round(3000/i)) == 0
        print(f'{i=}, {hide=}')
        if not hide:
            yield (int('3' + str(i)))

plt.axis([0,n/10,0,n*10])
plt.plot([x for x in x()])
plt.show()
