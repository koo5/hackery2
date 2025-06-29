import os, sys, time, json
import pty
from subprocess import check_output
import os,subprocess,time,shlex,logging, fire, ptyprocess

from ptyprocess import PtyProcess

log = logging.getLogger()
log.setLevel(logging.INFO)
# set logging to debug if the environment variable SHELL_DEBUG is set
hhh = logging.StreamHandler()
log.addHandler(hhh)
#hhh.setFormatter(logging.Formatter("%(asctime)s;%(levelname)s;%(message)s","%Y-%m-%d %H:%M:%S"))
if 'SHELL_DEBUG' in os.environ:
	log.setLevel(logging.DEBUG)


sq = shlex.quote
ss = shlex.split


def co(cmd):
	log.debug((cmd))
	return subprocess.check_output(cmd, text=True, universal_newlines=True)


def goe(cmd):
	return subprocess.run(cmd, text=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE, universal_newlines=True).stdout


def srun_get_retval(cmd):
	return subprocess.run(cmd, shell=True).returncode == 0


def srun(cmd):
	subprocess.run(cmd, shell=True)


def cc(cmd):
	log.debug((shlex.join(cmd)))
	return subprocess.check_call(cmd, text=True, universal_newlines=True)


def ccs(cmd):
	log.debug((cmd))
	return subprocess.check_call(cmd, shell=True, universal_newlines=True)


def ptyrun(cmd):
	print('|v')
	
	code = os.WEXITSTATUS(pty.spawn(['stdbuf', '-oL', '-eL'] + cmd))
	#code = os.waitstatus_to_exitcode(pty.spawn(['stdbuf', '-oL', '-eL'] + cmd))
	print('|^')
	return code == 0