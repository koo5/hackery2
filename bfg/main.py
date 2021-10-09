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
 


def get_ro_subvolumes(command_runner, subvolume):
	snapshots = {'by_received_uuid': {}, 'by_local_uuid': {}}
	for line in command_runner(['sudo', 'btrfs', 'subvolume', 'list', '-t', '-r', '-R', '-u', subvolume]).splitlines()[2:]:
		prerr(line)
		items = line.split()
		received_uuid = items[3]
		local_uuid = items[4]
		relpath = items[5]
		if received_uuid != '-':
			snapshots['by_received_uuid'][received_uuid] = relpath
		if local_uuid != '-':
			snapshots['by_local_uuid'][local_uuid] = relpath
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
				SNAPSHOTS_CONTAINER = Path(SNAPSHOTS_CONTAINER).absolute()

			if TAG is None:
				TAG = 'from_' + subprocess.check_output(['hostname'], text=True).strip()

			tss = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
			#tss = subprocess.check_output(['date', '-u', "+%Y-%m-%d_%H-%M-%S"], text=True).strip()
			ts = sanitize_filename(tss.replace(' ', '_'))

			SNAPSHOT = Path(str(SNAPSHOTS_CONTAINER) + '/' + TAG + '/' + ts)

		SNAPSHOT_PARENT = os.path.split(str(SNAPSHOT))[0]
		cmd(f'mkdir -p {SNAPSHOT_PARENT}')

		cmd(f'btrfs subvolume snapshot -r {VOL} {SNAPSHOT}')
		return str(SNAPSHOT)



	def commit_and_push(s, subvolume='/', remote_subvolume='/'):
		snapshot = s.commit(subvolume)
		parents = []
		for p in s.find_common_parents(subvolume, remote_subvolume):
			parents.append('-c')
			parents.append(p)
		local_cmd_runner(['sudo', 'btrfs', 'send'] + parents + [snapshot])
		
		pass
		

	def find_common_parents(s, subvolume='/', remote_subvolume='/'):
		
		remote_subvols = get_ro_subvolumes(remote_cmd_runner, remote_subvolume)['by_received_uuid']
		local_subvols = get_ro_subvolumes(local_cmd_runner, subvolume)['by_local_uuid']
		
		print('remote_subvols:')
		print(remote_subvols)
		print('local_subvols:')
		print(local_subvols)
		print("common_parents:")
		
		common_parents = []
		for k,v in local_subvols.items():
			if k in remote_subvols:
				common_parents.append(v)
		
		print(common_parents)
		return common_parents
		
		

	def commit_and_push_and_checkout(s, subvolume='/', remote_subvolume='/'):
		pass

	
	def commit_and_generate_patch(s):
		pass
		
		
def remote_cmd_runner(cmd):
	ssh = shlex.split('/opt/hpnssh/usr/bin/ssh   -p 2222   -o TCPRcvBufPoll=yes -o NoneSwitch=yes  -o NoneEnabled=yes     koom@10.0.0.20')
	return subprocess.check_output(ssh + cmd, text=True)

def local_cmd_runner(cmd):
	return subprocess.check_output(cmd, text=True)

def cmd(s):
	print(s)
	os.system(s)




if __name__ == '__main__':
        fire.Fire(Bfg)

