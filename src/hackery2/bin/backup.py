#!/usr/bin/env python3

from infra import *


def run(local=False, target='/bac4/'):

	# grab whatever info would not be transferred from ext4 partitions
	srun('snap list | sudo tee /root/snap_list')
	srun('ubuntu_selected_packages list | sudo tee /root/apt_list')
	#anything else? 
	#pause firefox? pause some vms?



	# set up target

	if local:
		ccs('sudo swipl -s /home/koom/hackery2/src/hackery2/bin/disks.pl  -g "start"')
		sshstr = ''
	else:
		r64_ip = get_r64_ip()
		ssh = get_hpnssh_executable()
		if r64_ip.startswith('10.'):
			insecure_speedups = '-o NoneSwitch=yes  -o NoneEnabled=yes'
		else:
			insecure_speedups = ''
		sshstr = f'--sshstr="{ssh}  -p 2222  -o TCPRcvBufPoll=yes {insecure_speedups}  koom@{r64_ip}"'



	# toplevel is where the bulk of the data lives, divided into subvolumes

	if hostname == 'hp':
		fss = [{
			'toplevel': '/mx500data',
			'subvols': ['backup', 'home', 'lean','leanpriv'],
		}]
	elif hostname == 'jj':
		fss = [{
			'toplevel': '/d2',
			'subvols': ['backup','images','images2','u'],
		}]
	elif hostname == 'r64':
		fss = [{
			'toplevel': '/',
			'subvols': ['/'],
		},{
			'toplevel': '/bac4',
			'subvols': ['lean', 'images_win'],
		}]



	# rsync ext4 filesystems into btrfs backup/ folder

	where = f"{fss[0]['toplevel']}/backup/root_ext4"
	if hostname == 'hp':
		rsync('/boot /root /etc /var/www /var/lib/docker/volumes', where)
	elif hostname == 'jj':
		rsync('/boot /home /root /etc /var/www /var/lib/docker/volumes /var/lib/snapd', where)

	
	# transfer btrfs subvolumes

	for fs in fss:
		toplevel = fs['toplevel']
		for subvol in fs['subvols']:
			target_subvol_name = subvol if subvol != '/' else '_root'
			ccs(f"""bfg --YES=true {sshstr} --LOCAL_FS_TOP_LEVEL_SUBVOL_MOUNT_POINT={toplevel} commit_and_push_and_checkout 			--SUBVOLUME={toplevel}/{subvol}/ --REMOTE_SUBVOLUME=/{target}/backup_{hostname}/{target_subvol_name}""")


def rsync(what,where):
	# todo figure out how to tell rsync not to try to sync what it can't sync, and then we can start checking its result
	srun(f'sudo rsync -v -a -S -v --progress -r --delete {what} {where}')

if __name__ == "__main__":
	fire.Fire(run)



"""
maybe we can make bfg smart enough to "detect" the filesystem that a given subvol resides in, and in turn
parse /etc/mtab to find if the filesystem is mounted with subvol=. If not, no "toplevel" parameter is needed.
Otherwise, it'd be prompted/required, or it could be assumed from other mtab lines.	
	
	
	
	
	
"""