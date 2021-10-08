#!/usr/bin/env python3



"""
1) snapshots should lie outside of the data directory (but configurable location).
2) ...
"""


from pathlib import Path
from pathvalidate import sanitize_filename
import sys,os
import time
import subprocess
import fire
import shlex





 
def prerr(*a):
	print(*a, file = sys.stderr)
 


def get_ro_subvolumes_with_received_uuid(command_runner, subvolume):
	snapshots = {}
	for line in command_runner(['sudo', 'btrfs', 'subvolume', 'list', '-t', '-r', '-R', subvolume]).splitlines()[2:]:
		prerr(line)
		items = line.split()
		received_uuid = items[3]
		relpath = items[4]
		if received_uuid != '-':
			snapshots[received_uuid] = relpath
	return snapshots





class Bfg:

	def commit(s, VOL='/', SNAPSHOTS_CONTAINER=None, TAG=None, SNAPSHOT=None):

		VOL = Path(VOL).absolute()

		if SNAPSHOT is not None:

			SNAPSHOT = Path(SNAPSHOT).absolute()
		else:

		
			if SNAPSHOTS_CONTAINER is None:
				SNAPSHOTS_CONTAINER = Path(str(VOL.parent) + '/.bfg_snapshots.' + VOL.parts[-1]).absolute()
			else:
				SNAPSHOTS_CONTAINER = SNAPSHOTS_CONTAINER.absolute()

			if TAG is None:
				TAG = 'from_' + subprocess.check_output(['hostname'], text=True).strip()

			tss = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
			#tss = subprocess.check_output(['date', '-u', "+%Y-%m-%d_%H-%M-%S"], text=True).strip()
			ts = sanitize_filename(tss.replace(' ', '_'))

			SNAPSHOT = Path(str(SNAPSHOTS_CONTAINER) + '/' + TAG + '/' + ts)

		SNAPSHOT_PARENT = os.path.split(str(SNAPSHOT))[0]
		cmd(f'mkdir -p {SNAPSHOT_PARENT}')

		cmd(f'btrfs subvolume snapshot -r {VOL} {SNAPSHOT}')



	def commit_and_push(s, subvolume='/', remote_subvolume='/'):
		
		def cmd_runner(cmd):
			ssh = shlex.split('/opt/hpnssh/usr/bin/ssh   -p 2222   -o TCPRcvBufPoll=yes -o NoneSwitch=yes  -o NoneEnabled=yes     koom@10.0.0.20')
			return subprocess.check_output(ssh + cmd, text=True)
		
		remote_subvols = get_ro_subvolumes_with_received_uuid(cmd_runner, remote_subvolume)
		
		print(remote_subvols)
		
		

	def commit_and_push_and_checkout(s, subvolume='/', remote_subvolume='/'):
		pass

	
	def commit_and_generate_patch(s):
		pass
		


def cmd(s):
	print(s)
	os.system(s)




if __name__ == '__main__':
        fire.Fire(Bfg)

