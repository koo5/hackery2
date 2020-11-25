#!/usr/bin/env python3
import click
import os
from datetime import datetime
import subprocess
import shlex


@click.command()
@click.option('-r', '--results_path', type=str)
def run(results_path):
	
	#os.path.expanduser
	base_path = (results_path)
	os.makedirs(base_path)

	while True:
		testsrun_dir_path = base_path + '/' + datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
		os.makedirs(testsrun_dir_path)
		with open(testsrun_dir_path+"/out.txt", "w") as file:
			subprocess.run(shlex.split('ctest  --debug  --output-on-failure'), stdout=file)
	


run()
