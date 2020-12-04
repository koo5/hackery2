#!/usr/bin/env python2

from subprocess import Popen,PIPE

out,err = Popen(['netstat','-antlp'],stdout=PIPE).communicate()

for l in out.splitlines():
    line = l.split()
    if '/' in line[-1]:
        p = line[-1].split('/')[0]
        line[-1] = str(p) + ' -> ' + open('/proc/'+p+'/cmdline','r').readline().split('-')[0]
    print '\t'.join(line)
