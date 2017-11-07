
#Using the "ptmx" interface is probably the best bet. Here is an example program that will attach to /dev/ptmx and trigger the creation of a /dev/pts/N device node that you can attach to from your application.

#For details, see "man pty".

#!/usr/bin/python
# Spawn pseudo-tty for input testing.
# Copyright 2010, Canonical, Ltd.
# Author: Kees Cook <kees@ubuntu.com>
# License: GPLv3
import os, sys, select

parent, child = os.openpty()
tty = os.ttyname(child)
os.system('stty cs8 -icanon -echo < %s' % (tty))

print tty

try:
    os.system('stty cs8 -icanon -echo < /dev/stdin')

    poller = select.poll()
    poller.register(parent, select.POLLIN)
    poller.register(sys.stdin, select.POLLIN)

    running = True
    while running:
        events = poller.poll(1000)
        for fd, event in events:
            if (select.POLLIN & event) > 0:
                chars = os.read(fd, 512)
                if fd == parent:
                    sys.stdout.write(chars)
                    sys.stdout.flush()
                else:
                    os.write(parent, chars)
finally:
    os.system('stty sane < /dev/stdin')


