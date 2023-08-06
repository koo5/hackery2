#!/usr/bin/env python3
import glob
from pathlib import Path

from infra import *


if hostname == 'r64':
	default_target_machine = None
	default_target_fs='/bac17/'
else:
	default_target_machine = 'r64'
	default_target_fs='/bac4/'


def run(target_machine=default_target_machine, target_fs=default_target_fs):
	"""back up the machine that this script runs on"""



	# grab whatever info would not be transferred from ext4 partitions
	srun('snap list | sudo tee /root/snap_list')
	srun('ubuntu_selected_packages list | sudo tee /root/apt_list')
	#anything else? 
	#pause firefox? pause some vms?
	fss = get_filesystems()
	rsync_ext4_filesystems_into_backup_folder(fss)
	add_backup_subvols(fss[0])
	sshstr = set_up_target(target_machine)
	transfer_btrfs_subvolumes(sshstr, fss, target_fs)




def set_up_target(target_machine):

	if target_machine is None:
		ccs('sudo swipl -s /home/koom/hackery2/src/hackery2/bin/disks.pl  -g "start"')
		sshstr = ''
	elif target_machine == 'r64':
		r64_ip = get_r64_ip()
		ssh = get_hpnssh_executable()
		if r64_ip.startswith('10.'):
			insecure_speedups = '-o NoneSwitch=yes  -o NoneEnabled=yes'
		else:
			insecure_speedups = ''
		sshstr = f'--sshstr="{ssh}  -p 2222  -o TCPRcvBufPoll=yes {insecure_speedups}  koom@{r64_ip}"'
	else:
		raise Exception('unsupported')
	return sshstr



def get_filesystems():
	# each of my machines has a big btrfs disk where the bulk of my data lives, divided into subvolumes
	# each machine also has a small ext4 or btrfs disk where the OS lives
	# we rsync ext4 disks into a subvolume on the btrfs disk, and then use bfg to transfer the btrfs subvolumes
	# but maybe in future we should just rsync them to the target btrfs filesystem directly

	if hostname == 'hp':
		fss = [{
			'toplevel': '/mx500data',
			'subvols': m(['home', 'lean','leanpriv']),
		}]
	elif hostname == 'jj':
		fss = [{
			'toplevel': '/d2',
			'subvols': m(['images','images2','u']),
		}]
	elif hostname == 'r64':
		fss = [{
			'toplevel': '/bac4',
			'subvols': m(['lean', 'images_win', 'cold'])
		},
		{
			'toplevel': '/',
			'subvols': m(['/']),
		}]
	return fss


def transfer_btrfs_subvolumes(sshstr, fss, target_fs):
	for fs in fss:
		toplevel = fs['toplevel']
		for subvol in fs['subvols']:
			print(subvol)

			name = subvol['name']
			source_path = subvol['source_path']
			target_dir = subvol['target_dir']

			target_subvol_name = name if name != '/' else '_root'

			ccs(f"""bfg --YES=true {sshstr} --LOCAL_FS_TOP_LEVEL_SUBVOL_MOUNT_POINT={toplevel} commit_and_push_and_checkout 			--SUBVOLUME={toplevel}/{source_path}{name}/ --REMOTE_SUBVOLUME=/{target_fs}/backups/{target_dir}/{target_subvol_name}""")


def rsync_ext4_filesystems_into_backup_folder(fss):
	# it probably makes sense to eventually rsync straight to the backup media
	if hostname == 'hp':
		rsync(fss, '/boot /root /etc /var/www /var/lib/docker/volumes')
	elif hostname == 'jj':
		rsync(fss, '/boot /home /root /etc /var/www /var/lib/docker/volumes /var/lib/snapd')



def rsync(fss, what):
	# this path corresponds to the structure expected by add_backup_subvols and also created by transfer_btrfs_subvolumes, that is, /mountpoint/backups/hostname/subvol
	where = f"{fss[0]['toplevel']}/backups/{hostname}/root_ext4"
	if not Path(where).exists():
		ccs(f'sudo btrfs sub create {where}')
	# todo figure out how to tell rsync not to try to sync what it can't sync, and then we can start checking its result
	srun(f'sudo rsync -v -a -S -v --progress -r --delete {what} {where}')


def add_backup_subvols(fs):
	# this could be replaced with a recursive search that stops at subvolumes (and yields them). There is on inherent need to only support a flat structure.
	
	#for host in glob.glob('*', root_dir=fs['toplevel'] + '/backups/'):
	os.chdir(fs['toplevel'] + '/backups/')
	for host in glob.glob('*'):
		os.chdir(fs['toplevel'] + '/backups/' + host)
		fs['subvols'] += [{'target_dir': host,
						  'name': name,
						  'source_path': '/backups/' + host + '/'} for name in
						  #glob.glob('*', root_dir=fs['toplevel'] + '/backups/' + host)]
						  glob.glob('*')]



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
	
	
	
	
	
"""
