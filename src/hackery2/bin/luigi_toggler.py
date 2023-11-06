#!/usr/bin/env python3

import subprocess, requests

on = int(subprocess.check_output(['xprintidle'])) > 1000*60*2
un = ('un' if on else '')
cmd = f'http://localhost:8082/api/{un}pause'
print(f'{cmd}')
requests.get(cmd)
