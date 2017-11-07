


#Using the "ptmx" interface is probably the best bet. Here is an example program that will attach to /dev/ptmx and trigger the creation of a /dev/pts/N device node that you can attach to from your application.

#For details, see "man pty".

#!/usr/bin/python3
# Spawn pseudo-tty for input testing.
# Copyright 2010, Canonical, Ltd.
# Author: Kees Cook <kees@ubuntu.com>
# License: GPLv3
import os, sys, select



import serial
serial = serial.Serial(parity=serial.PARITY_EVEN, bytesize=serial.SEVENBITS)
serial.port = sys.argv[1]
serial.baudrate = 57600
serial.timeout = 0
serial.rts = True
serial.dtr = True
serial.open()




parent, child = os.openpty()
tty = os.ttyname(child)

stty = "stty 57600 cs7 evenp -cstopb -icanon -echo < "
os.system(stty+'%s' % (tty))

print (tty)

try:
    os.system(stty+'/dev/stdin')

    poller = select.poll()
    poller.register(parent, select.POLLIN)
    poller.register(sys.stdin, select.POLLIN)
    poller.register(serial.fileno(), select.POLLIN)
    running = True
    while running:
        events = poller.poll(1000)
        for fd, event in events:
            if (select.POLLIN & event) > 0:
                chars = os.read(fd, 100)
                if fd == parent:
                    sys.stdout.write(" out>>>")
                    print(chars)
                    #sys.stdout.write(chars.hex())
                    sys.stdout.flush()
                    serial.write(chars)
                    serial.flush()
                elif fd == serial.fileno():
                    sys.stdout.write(" IN<<<")
                    sys.stdout.write(chars.hex())
                    sys.stdout.flush()
                    os.write(parent, chars)
finally:
    os.system('stty sane < /dev/stdin')


