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









class Bfg:


	def commit_and_push(s, fs_root_mount_point='/', subvolume='/', remote_subvolume='/'):
		snapshot = s.commit(subvolume)
		s.push(fs_root_mount_point, subvolume, snapshot, remote_subvolume)
		
	"""
	def local_checkout(s, what, where):


	def local_stash(s, what):
		
	
	
	
	"""

	def local_make_ro_snapshot(VOLe, SNAPSHOT):
		SNAPSHOT_PARENT = os.path.split((SNAPSHOT))[0]
		cmd(f'mkdir -p {SNAPSHOT_PARENT}')
		cmd(f'btrfs subvolume snapshot -r {VOL} {SNAPSHOT}')



	def commit(s, VOL='/', SNAPSHOTS_CONTAINER=None, TAG=None, SNAPSHOT=None):

		VOL = Path(VOL).absolute()

		if SNAPSHOT is not None:
			SNAPSHOT = Path(SNAPSHOT).absolute()
		else:
			SNAPSHOT = snapshot_path(VOL, TAG)

		SNAPSHOT_PARENT = os.path.split((SNAPSHOT))[0]
		cmd(f'mkdir -p {SNAPSHOT_PARENT}')
		cmd(f'btrfs subvolume snapshot -r {VOL} {SNAPSHOT}')

		return (SNAPSHOT)

		
		
	def push(s, fs_root_mount_point, subvolume, snapshot, remote_subvolume):
		SNAPSHOT_PARENT = snapshot_parent_dir(Path(remote_subvolume))
		remote_cmd_runner(['sudo', 'mkdir', '-p', str(SNAPSHOT_PARENT)])

		parents = []
		for p in s.find_common_parents(fs_root_mount_point, subvolume, remote_subvolume):
			parents.append('-c')
			parents.append(p)
			
		cmd = shlex.join(['sudo', 'btrfs', 'send'] + parents + [snapshot]) + '|' + sshstr + " sudo btrfs receive " + str(SNAPSHOT_PARENT)
		prerr((cmd))
																														   
		subprocess.check_call(cmd, shell=True)
		
		# remote_cmd_runner('sudo', 'btrfs', 'receive'] + [where])
		pass
		

	def find_common_parents(s, fs_root_mount_point='/', subvolume='/', remote_subvolume='/'):
		
		remote_subvols = get_ro_subvolumes(remote_cmd_runner, remote_subvolume)['by_received_uuid']
		local_subvols = get_ro_subvolumes(local_cmd_runner, subvolume)['by_local_uuid']
		
		#print('remote_subvols:')
		#print(remote_subvols)
		#print('local_subvols:')
		#print(local_subvols)
		#print("common_parents:")
		
		common_parents = []
		for k,v in local_subvols.items():
			if k in remote_subvols:
				abspath = fs_root_mount_point + '/' + local_cmd_runner(['btrfs', 'ins', 'sub', v, subvolume]).strip()
				common_parents.append(abspath)
		
		#print(common_parents)
		return common_parents
		
		

	def commit_and_push_and_checkout(s, subvolume='/', remote_subvolume='/'):
		pass

	
	def commit_and_generate_patch(s):
		pass
		
		
sshstr = '/opt/hpnssh/usr/bin/ssh   -p 2222   -o TCPRcvBufPoll=yes -o NoneSwitch=yes  -o NoneEnabled=yes     koom@10.0.0.20'		
		
def remote_cmd_runner(cmd):
	ssh = shlex.split(sshstr)
	cmd2 = ssh + cmd
	prerr(cmd2)
	return subprocess.check_output(cmd2, text=True)

def local_cmd_runner(cmd):
	return subprocess.check_output(cmd, text=True)

def cmd(s):
	print(s)
	try:
		subprocess.check_call(shlex.split(s))
	except Exception as e:
		print(e)
		exit(1)


def snapshot_parent_dir(VOL):
		return Path(str(VOL.parent) + '/.bfg_snapshots.' + VOL.parts[-1]).absolute()


def snapshot_path(VOL, TAG):
	parent = snapshot_parent_dir(VOL)
	
	tss = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
	#tss = subprocess.check_output(['date', '-u', "+%Y-%m-%d_%H-%M-%S"], text=True).strip()
	ts = sanitize_filename(tss.replace(' ', '_'))

	if TAG is None:
		TAG = 'from_' + subprocess.check_output(['hostname'], text=True).strip()

	return str(Path(str(parent) + '/' + ts + '_' + TAG))

 
def prerr(*a):
	print(*a, file = sys.stderr)
 


def get_ro_subvolumes(command_runner, subvolume):
	snapshots = {'by_received_uuid': {}, 'by_local_uuid': {}}
	for line in command_runner(['sudo', 'btrfs', 'subvolume', 'list', '-t', '-r', '-R', '-u', subvolume]).splitlines()[2:]:
		#prerr(line)
		items = line.split()
		received_uuid = items[3]
		local_uuid = items[4]
		subvol_id = items[0]
		if received_uuid != '-':
			snapshots['by_received_uuid'][received_uuid] = subvol_id
		if local_uuid != '-':
			snapshots['by_local_uuid'][local_uuid] = subvol_id
	return snapshots




if __name__ == '__main__':
        fire.Fire(Bfg)

