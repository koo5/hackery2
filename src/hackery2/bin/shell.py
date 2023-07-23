import os, sys, time, json
import pty
from subprocess import check_output
import os,subprocess,time,shlex,logging, fire, ptyprocess

from ptyprocess import PtyProcess

l = logging.getLogger()
l.setLevel(logging.DEBUG)
l.addHandler(logging.StreamHandler())


sq = shlex.quote
ss = shlex.split


def co(cmd):
	return subprocess.check_output(cmd, text=True, universal_newlines=True)


def goe(cmd):
	return subprocess.run(cmd, text=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE, universal_newlines=True).stdout


def srun_get_retval(cmd):
	return subprocess.run(cmd, shell=True).returncode == 0


def srun(cmd):
	subprocess.run(cmd, shell=True)


def cc(cmd):
	return subprocess.check_call(cmd, text=True, universal_newlines=True)


def ccs(cmd):
	return subprocess.check_call(cmd, shell=True, universal_newlines=True)


def ptyrun(cmd):
	print('|v')
	
	code = os.WEXITSTATUS(pty.spawn(['stdbuf', '-oL', '-eL'] + cmd))
	#code = os.waitstatus_to_exitcode(pty.spawn(['stdbuf', '-oL', '-eL'] + cmd))
	print('|^')
	return code == 0