#!/usr/bin/env python3


"""
install:
 pip install fire ptyprocess


notes:

--local
"it seems that this would be preferred to snapper or similar, as it would also backup ext4 filesystems, cloud machines, etc, and do everything from the same confguration used for actual remote backups.
it's just needed to set this up with cron.

cron on backup servir:
every 1h: ~/backup_clouds.sh; backup.sh --local

cron on workstation:
every 1h: backup.sh
...too many disk spinups for backup machine?

todo:
bfg fix common parent lookup for toplevel subvol.
track snapshot origin in .bfg/bfg.json in snapshot. why?
send all snapshots in succession.

"""



import glob
import pathlib
from pathlib import Path

from infra import *


def check_if_mounted(sshstr, target_fs):
	for line in co(shlex.split(f'{sshstr} cat /etc/mtab')).strip().split('\n'):
		print(line)
		items = line.split()
		if items[1] +'/' == target_fs:
			return
	raise Exception(f'{target_fs} not mounted')


def run(source='host', target_machine=None, target_fs=None, local=False):
	"""back up the source (host or clouds)"""


	if hostname == 'r64':
		default_target_machine = None
		default_target_fs='/bac17/'
	else:
		default_target_machine = 'r64'
		default_target_fs='/bac4/'


	if source == 'clouds':
		default_target_fs='/bac4/'

	if target_machine is None:
		target_machine = default_target_machine
	if target_fs is None:
		target_fs = default_target_fs

	if target_machine == '':
		print('target_machine = None')
		target_machine = None
	print(f'target_machine = {target_machine}')

	sshstr,sshstr2 = set_up_target(target_machine)

	if not local:
		check_if_mounted(sshstr, target_fs)

	if source != 'clouds':
		# grab whatever info would not be transferred from ext4 partitions
		#srun('sudo snap save')
		srun('snap list | sudo tee /root/snap_list')
		srun('ubuntu_selected_packages list | sudo tee /root/apt_list')
		#anything else?
		#pause firefox? pause some vms?
		fss = get_filesystems()

	if source == 'clouds' and hostname == 'r64':
		backup_vpss(fss[0]['toplevel'])

	rsync_ext4_filesystems_into_backup_folder(fss)

	if not local:
		"""no point in snapshotting backup subvols if we're not going to transfer them"""
		add_backup_subvols(fss[0])

	transfer_btrfs_subvolumes(sshstr2, fss, target_fs, local)



def set_up_target(target_machine):

	if target_machine is None:
		ccs('sudo swipl -s /home/koom/hackery2/src/hackery2/bin/disks.pl  -g "start"')
		sshstr = ''
		sshstr2 = ''
	elif target_machine == 'r64':
		r64_ip = get_r64_ip()
		ssh = get_hpnssh_executable()
		if r64_ip.startswith('10.'):
			insecure_speedups = '-o NoneSwitch=yes  -o NoneEnabled=yes'
		else:
			insecure_speedups = ''
		sshstr = f'{ssh}  -p 2222  -o TCPRcvBufPoll=yes {insecure_speedups}  koom@{r64_ip}'
		sshstr2 = '--sshstr="' + sshstr + '"'
	else:
		raise Exception('unsupported')
	return sshstr, sshstr2



def get_filesystems():
	# each of my machines has a big btrfs disk where the bulk of my data lives, divided into subvolumes
	# each machine also has a small ext4 or btrfs disk where the OS lives
	# we rsync ext4 disks into a subvolume on the btrfs disk, and then use bfg to transfer the btrfs subvolumes
	# but maybe in future we should just rsync them to the target btrfs filesystem directly

	if hostname == 'hp':
		fss = [{
			'toplevel': '/mx500data',
			'subvols': m(['home', 'lean','leanpriv', 'dev3']),
		}]
	elif hostname == 'jj':
		fss = [{
			'toplevel': '/d2',
			'subvols': m(['u', 'dev3', 'home', '/']),
		}]
	elif hostname == 'r64':
		fss = [{
			'toplevel': '/bac4',
			'subvols': m(['cold', 'images_win'])
		},
		{
			'toplevel': '/',
			'subvols': m(['/']),
		}]
	return fss


def transfer_btrfs_subvolumes(sshstr, fss, target_fs, local):
	for fs in fss:
		toplevel = fs['toplevel']
		for subvol in fs['subvols']:
			print(subvol)

			name = subvol['name']
			source_path = subvol['source_path']
			target_dir = subvol['target_dir']

			target_subvol_name = name if name != '/' else '_root'

			ccs(f"""date""")
			if local:
				ccs(f"""bfg --YES=true --LOCAL_FS_TOP_LEVEL_SUBVOL_MOUNT_POINT={toplevel} local_commit --SUBVOLUME={toplevel}/{source_path}{name}/ """)
			else:
				ccs(f"""bfg --YES=true {sshstr} --LOCAL_FS_TOP_LEVEL_SUBVOL_MOUNT_POINT={toplevel} commit_and_push_and_checkout --SUBVOLUME={toplevel}/{source_path}{name}/ --REMOTE_SUBVOLUME=/{target_fs}/backups/{target_dir}/{target_subvol_name}""")
			ccs(f"""date""")
			print('', file = sys.stderr)



def rsync_ext4_filesystems_into_backup_folder(fss):
	# it probably makes sense to eventually rsync straight to the backup media
	if hostname == 'hp':
		rsync(fss, '/boot /root /etc /var/www /var/lib/docker/volumes')
	elif hostname == 'jj':
		rsync(fss, '/boot /root /etc')



def rsync(fss, what, name='root_ext4'):
	# this path corresponds to the structure expected by add_backup_subvols and also created by transfer_btrfs_subvolumes, that is, /mountpoint/backups/hostname/subvol
	where = f"{fss[0]['toplevel']}/backups/{hostname}/{name}"
	if not Path(where).exists():
		ccs(f'sudo btrfs sub create {where}')
	# todo figure out how to tell rsync not to try to sync what it can't sync, and then we can start checking its results
	srun(f'sudo rsync --one-file-system -v -a -S -v --progress -r --delete {what} {where}')



import getpass
import os
import grp




def backup_vpss(toplevel='/bac4'):
	for cloud_host in json.load(open(os.path.expanduser('~/secrets.json')))['cloud_servers']:
		backup_vps(toplevel, cloud_host)



def backup_vps(toplevel, cloud_host):

	where = pathlib.Path(f"{toplevel}/backups/{cloud_host}/root")

	#os.makedirs(where.parent, exist_ok=True)
	ccs(f'sudo mkdir -p {where.parent}')
	
	if not Path(where).exists():
		ccs(f'sudo btrfs sub create {where}')
	
	username = getpass.getuser()
	group_name = grp.getgrgid(os.getgid()).gr_name
	
	ccs(f'sudo chown {username}:{group_name} {where}')

	ccs(f'backup_vps.sh {cloud_host} {where}; true')



def add_backup_subvols(fs):
	# this could be replaced with a recursive search that stops at subvolumes (and yields them). There is no inherent need to only support a flat structure.
	# gotta do something like sudo btrfs subvolume list -q -t -R -u -a $fsroot | grep live | grep -v ".bfg_snapshots"
	# but preferably using bfg's facilities.	
	
	os.chdir(fs['toplevel'] + '/backups/')
	for host in glob.glob('*'):
		os.chdir(fs['toplevel'] + '/backups/' + host)
		fs['subvols'] += [{'target_dir': host,
						  'name': name[:-1],
						  'source_path': '/backups/' + host + '/'} for name in
						  glob.glob('*/')]



def m(subvols):
	"""return subvol specifications for a machine's filesystem"""
	return [{'target_dir': hostname,
			'name':subvol,
			'source_path':''} for subvol in subvols]



if __name__ == "__main__":
	fire.Fire(run)



"""
maybe we can make bfg smart enough to "detect" the filesystem that a given subvol resides in, and in turn
parse /etc/mtab to find if the filesystem is mounted with subvol=. If not, no "toplevel" parameter is needed.
Otherwise, it'd be prompted/required, or it could be assumed from other mtab lines.	
	
	
	
	
	
	if hostname == 'dev3':
		cr(cwd='/home/koom/.config', cmd='git add .; git commit -m "auto commit"')

def cr(cwd, cmd):
	try:
		cc(cwd=cwd, cmd=cmd)
	except Exception as e:
		report(e)
"""
