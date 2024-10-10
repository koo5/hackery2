#!/usr/bin/env python3


# control luigi and core_control


import subprocess, requests, logging


logging.basicConfig(level=logging.DEBUG)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


out = subprocess.check_output(['uptime'])
log.info(out)

out = subprocess.check_output(['xprintidle'], env={'DISPLAY':':0'})
out = int(out)
log.info('xprintidle: ' + str(out) + 'ms')

fun_on = out > 1000*60*2

log.info(f'fun is {fun_on}')

un = ('un' if fun_on else '')
cmd = f'http://localhost:8082/api/{un}pause'
log.info(f'{cmd}')
try:
    requests.get(cmd, timeout=3)
except:
    pass

cores = 48 if fun_on else 5
cmd = 'http://192.168.122.128:1111/set_cores={}'.format(cores)
log.info(f'{cmd}')
try:
    requests.get(cmd, timeout=3)
except:
    pass

