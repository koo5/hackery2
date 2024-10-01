#!/usr/bin/env python3

import subprocess, requests

# control luigi and core_control

on = int(subprocess.check_output(['xprintidle'])) > 1000*60*2
un = ('un' if on else '')
cmd = f'http://localhost:8082/api/{un}pause'
print(f'{cmd}')
try:
    requests.get(cmd, timeout=3)
except:
    pass

cores = 24 if on else 10
cmd = 'http://192.168.122.128:1111/set_cores={}'.format(cores)
print(f'{cmd}')
try:
    requests.get(cmd, timeout=3)
except:
    pass

