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
import logging
log = logging.getLogger()
log.setLevel(logging.INFO)

_use_db = True

def run(source='host', target_machine=None, target_fs=None, local=False):

	default_target_machine = 'r64'
	default_target_fs='/bac18/'

	if hostname == 'r64':
		default_target_machine = None
		default_target_fs = '/bac19/'
	
	if target_machine is None:
		target_machine = default_target_machine
	if target_fs is None:
		target_fs = default_target_fs

	if target_machine == '':
		print('target_machine = None')
		target_machine = None

	if not local:
		print(f'target_machine = {target_machine}')
		sshstr, sshstr2 = set_up_target(target_machine)
	else:
		sshstr = ''
		sshstr2 = ''

	if not local:
		check_if_mounted(sshstr, target_fs)


	sync_stuff(hostname)

	# grab whatever info would not be transferred from ext4 partitions
	#srun('sudo snap save')
	srun('snap list | sudo tee /root/snap_list')
	srun('ubuntu_selected_packages list | sudo tee /root/apt_list')

	#anything else?
	#pause firefox? pause some vms?

	fss = get_filesystems()


	import_noncows(source, hostname, target_fs, fss)
	print()
	print('---done import_noncows---')
	print()
	# todo: then there's no need to add_backup_subvols if local==True
	add_backup_subvols(fss[-1])

	transfer_btrfs_subvolumes(sshstr, sshstr2, fss, target_fs, local)


def sync_stuff(hostname):
	where = f'/d/sync/jj/host/{hostname}/'
	what = f'/home/koom/.local/share/fish/fish_history'
	cc(ss(f'mkdir -p {where}'))

	srun(f'rsync --one-file-system -v -a -S -v --progress -r --delete {what} {where}')


def import_noncows(source, hostname, target_fs, fss):
	"""
	todo: we should make a snapshot of each subvol right after the transfer is finished. This will parallel how btrfs snapshots are "imported".
	"""

	if hostname == 'r64':
		backup_vpss(target_fs)

	rsync_ext4_filesystems_into_backup_folder(fss)


def set_up_target(target_machine):

	if target_machine is None:
		ccs('sudo swipl -s /home/koom/hackery2/src/hackery2/bin/disks.pl  -g "start"')
		return  '', ''

	insecure_speedups = ''
	ssh = get_hpnssh_executable()

	if target_machine == 'r64.internal':
		insecure_speedups = '-o NoneSwitch=yes  -o NoneEnabled=yes'
		long_ssh = ' -o ServerAliveInterval=600 -o ServerAliveCountMax=999999  -o TCPKeepAlive=no  '
		sshstr = f'{ssh}  -p 2222  -o TCPRcvBufPoll=yes {long_ssh} {insecure_speedups} koom@r64.internal'

	if target_machine == 'jj.internal':
		insecure_speedups = '-o NoneSwitch=yes  -o NoneEnabled=yes'
		long_ssh = ' -o ServerAliveInterval=600 -o ServerAliveCountMax=999999  -o TCPKeepAlive=no  '
		sshstr = f'{ssh}  -p 2222  -o TCPRcvBufPoll=yes {long_ssh} {insecure_speedups} koom@jj.internal'


	elif target_machine == 'jj':
		long_ssh = ' -o ServerAliveInterval=600 -o ServerAliveCountMax=999999  -o TCPKeepAlive=no  '
		sshstr = f'{ssh}  -p 2222  -o TCPRcvBufPoll=yes {long_ssh} {insecure_speedups} koom@jj'


	elif target_machine == 'r64':
		r64_ip = get_r64_ip()
		if r64_ip.startswith('10.'):
			insecure_speedups = '-o NoneSwitch=yes  -o NoneEnabled=yes'
		sshstr = f'{ssh}  -p 2222  -o TCPRcvBufPoll=yes {insecure_speedups} koom@{r64_ip}'

	else:
		raise Exception('unsupported')


	sshstr2 = '--sshstr="' + sshstr + '"'
	return sshstr, sshstr2



def get_filesystems():
	# each of my machines has a big btrfs disk where the bulk of my data lives, divided into subvolumes
	# each machine also has a small ext4 or btrfs disk where the OS lives
	# we rsync ext4 disks into a subvolume on the btrfs disk, and then use bfg to transfer the btrfs subvolumes
	# but maybe in future we should just rsync them to the target btrfs filesystem directly

	global _use_db

	if hostname == 'hp':
		fss = [{
			'toplevel': '/mx500data',
			'subvols': m(['home', 'lean','leanpriv', 'dev3']),
		}]
	elif hostname == 'jj':
		fss = [
			{
				'toplevel': '/var',
				'subvols': m(['/']),
			},
			{
				'toplevel': '/d2',
				'subvols': m(['u', 'dev3', 'home', '/']),
			},
		]

	elif hostname == 'r64':
		fss = [{
			'toplevel': '/bac4',
			'subvols': m(['cold'])
		},
		{
			'toplevel': '/home/koom/Sync',
			'subvols': m(['/'])
		},
		{
			'toplevel': '/',
			'subvols': m(['/']),
		},
		{
			'toplevel': '/bac18',
			'subvols': m(['/']),
		}]
	elif hostname == 't14':
		fss = [{
			'toplevel': '/',
			'subvols': m(['/'])
		},
		{
			'toplevel': '/data',
			'subvols': m(['/']),
		}]
	elif hostname == 'c1':
		_use_db = False
		fss = [{
			'toplevel': '/',
			'subvols': m(['/'])
		},
		{
			'toplevel': '/home/koom',
			'subvols': m(['/']),
		}]
	return fss


def transfer_btrfs_subvolumes(sshstr, sshstr2, fss, target_fs, local):
	for fs in fss:
		toplevel = fs['toplevel']
		for subvol in fs['subvols']:
			print('backup ' + toplevel + ' ' + subvol['name'])

			name = subvol['name']
			source_path = subvol['source_path']
			target_dir = subvol['target_dir']
			target_subvol_name = name if name != '/' else toplevel.replace('/', '_') + '_root'
			subvol_path = Path(f"{toplevel}/{source_path}{name}")
			#ccs(f"""date""")
			if local:
				ccs(f"""bfg --YES=true local_commit --SUBVOL={subvol_path} """)
			else:
				remote_subvol_path = Path(target_fs)/'backups'/target_dir/target_subvol_name
				ccs(f"""bfg --YES=true {sshstr2} commit_and_push_and_checkout --SUBVOL={subvol_path} --REMOTE_SUBVOL={remote_subvol_path} """)
			#ccs(f"""date""")
			print('', file = sys.stderr)
		if _use_db:
			ccs(f"""bfg --YES=true --FS={toplevel} update_db """)
			if not local:
				ccs(f"""{sshstr} bfg --YES=true --FS={target_fs} update_db """)

		#ccs(f"""bfg prune_stashes --YES=true --FS={target_fs} """)

		for subvol in fs['subvols']:
			log.debug(f'pruning {subvol=}')
			name = subvol['name']
			source_path = subvol['source_path']
			target_dir = subvol['target_dir']
			target_subvol_name = name if name != '/' else toplevel.replace('/', '_') + '_root'
			subvol_path = Path(f"{toplevel}/{source_path}{name}")
			ccs(f"""bfg prune_local --DB={_use_db} --YES=true  --SUBVOL={subvol_path} """)
			if not local:
				remote_subvol_path = Path(target_fs)/'backups'/target_dir/target_subvol_name
				ccs(f"""bfg {sshstr2} prune_remote  --YES=true  --LOCAL_SUBVOL={subvol_path} --REMOTE_SUBVOL={remote_subvol_path}""")

		print('', file = sys.stderr)



def rsync_ext4_filesystems_into_backup_folder(fss):
	# it probably makes sense to eventually rsync straight to the backup media
	if hostname == 'hp':
		rsync(fss, '/boot /root /etc /var/www /var/lib/docker/volumes')
	elif hostname == 'jj':
		rsync(fss, '/boot /root /etc')



def rsync(fss, what, name='root_ext4'):
	# this path corresponds to the structure expected by add_backup_subvols and also created by transfer_btrfs_subvolumes, that is, /mountpoint/backups/hostname/subvol
	where = f"{fss[-1]['toplevel']}/backups/{hostname}/{name}"
	if not Path(where).exists():
		ccs(f'sudo btrfs sub create {where}')
	# todo figure out how to tell rsync not to try to sync what it can't sync, and then we can start checking its results
	srun(f'sudo rsync --one-file-system -v -a -S -v --progress -r --delete {what} {where}')



import getpass
import os
import grp




def backup_vpss(target_fs):
	for cloud_host in json.load(open(os.path.expanduser('~/secrets.json')))['cloud_servers']:
		backup_vps(target_fs, cloud_host)



def backup_vps(target_fs, cloud_host):

	where = pathlib.Path(f"{target_fs}/backups/{cloud_host}/root")

	#os.makedirs(where.parent, exist_ok=True)
	ccs(f'sudo mkdir -p {where.parent}')

	if not Path(where).exists():
		ccs(f'sudo btrfs sub create {where}')

	username = getpass.getuser()
	group_name = grp.getgrgid(os.getgid()).gr_name

	ccs(f'sudo chown {username}:{group_name} {where}')
	ccs(f'backup_vps.sh {cloud_host} {where}; true')
	ccs(f'bfg local_commit --SUBVOL={where}')


def add_backup_subvols(fs):
	# this could be replaced with a recursive search that stops at subvolumes (and yields them). There is no inherent need to only support a flat structure.
	# gotta do something like sudo btrfs subvolume list -q -t -R -u -a $fsroot | grep live | grep -v ".bfg_snapshots"
	# but preferably using bfg's facilities.	

	d = fs['toplevel'] + '/backups/'
	print('looking for backup subvols in ' + d)
	if not Path(d).exists():
		print('no backups folder')
		return
	os.chdir(d)
	for host in glob.glob('*'):
		print('found backup subvol ' + host)
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



def check_if_mounted(sshstr, target_fs):
	for line in co(shlex.split(f'{sshstr} cat /etc/mtab')).strip().split('\n'):
		print(line)
		items = line.split()
		if items[1] +'/' == target_fs:
			return
	raise Exception(f'{target_fs} not mounted')



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
