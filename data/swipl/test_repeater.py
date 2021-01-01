#!/usr/bin/env python3
import click
import os
from datetime import datetime
import subprocess
import shlex


# grep -r "failed out" test_runs* | sort |  sed 's/:/ /'


def cmd(out_file, cmd):
	out_file.flush()
	out_file.write('>' + cmd + '\n')
	out_file.flush()
	subprocess.run(shlex.split(cmd), stdout=out_file, stderr=out_file)
	out_file.write('\n')
	out_file.flush()
	

@click.command()
@click.option('-r', '--results_path', type=str, default='../test_runs')
@click.option('-p', '--ctest_parallelism', type=int, default=1)
def run(results_path,ctest_parallelism):
	
	#os.path.expanduser
	base_path = (results_path)
	os.makedirs(base_path, exist_ok=True)

	while True:
		testsrun_dir_path = base_path + '/' + datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S.%f')
		os.makedirs(testsrun_dir_path)
		with open(testsrun_dir_path+"/out.txt", "w") as f:
			cmd(f,'bash -c "git show --pretty=oneline | head -n 1"')
			cmd(f,'git status')
			cmd(f,'ctest -j '+str(ctest_parallelism)+' --output-on-failure')
			cmd(f,'gcc -v')
			cmd(f,'uname -a')
			cmd(f,'lscpu')
			
run()

