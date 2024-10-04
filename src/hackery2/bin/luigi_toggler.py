#!/usr/bin/env python3

import subprocess, requests, logging


logging.basicConfig(level=logging.DEBUG)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


# control luigi and core_control

out = subprocess.check_output(['xprintidle'], env={'DISPLAY':':0'})
log.info(out)

on = int(out) > 1000*60*2

log.info(f'fun is {on}')

un = ('un' if on else '')
cmd = f'http://localhost:8082/api/{un}pause'
log.info(f'{cmd}')
try:
    requests.get(cmd, timeout=3)
except:
    pass

cores = 24 if on else 5
cmd = 'http://192.168.122.128:1111/set_cores={}'.format(cores)
log.info(f'{cmd}')
try:
    requests.get(cmd, timeout=3)
except:
    pass

