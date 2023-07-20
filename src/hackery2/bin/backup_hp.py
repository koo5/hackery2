#!/usr/bin/env python3

from infra import *


def run(local=False, target_path='/bac4/'):
	if local:
		ccs('sudo swipl -s /home/koom/hackery2/src/hackery2/bin/disks.pl  -g "start"')

	srun('snap list | sudo tee /root/snap_list')
	srun('ubuntu_selected_packages list | sudo tee /root/apt_list')
	
	if hostname == 'hp':
		where = '/mx500data/backup_hp_ext'
		what = '/boot /root /etc /var/www /var/lib/docker/volumes'
		srun('sudo rsync -v -a -S -v --progress -r --delete {what} {where}')
	elif hostname == 'jj':
		where = '/d2/backup/jj_ext'
		what = '/boot /home /root /etc /var/www /var/lib/docker/volumes /var/lib/snapd'
		srun('sudo rsync -v -a -S -v --progress -r --delete {what} {where}')

	if local:
		sshstr = ''
	else:
		r64_ip = get_r64_ip()
		ssh = get_hpnssh_executable()
		if r64_ip.startswith('10.'):
			insecure_speedups = '-o NoneSwitch=yes  -o NoneEnabled=yes'
		else:
			insecure_speedups = ''
		sshstr = f'--sshstr="{ssh}  -p 2222  -o TCPRcvBufPoll=yes {insecure_speedups}  koom@{ip}"'

	if hostname == 'hp':
		subvols = ['backup','images','images2','u']
		toplevel = '/mx500data'
		data = '/mx500data'
	elif hostname == 'jj':
		subvols = ['backup','images','images2','u']
		toplevel = '/d2'
		data = '/d2'

	for subvol in :
		ccs(f"""bfg --YES=true {sshstr} --LOCAL_FS_TOP_LEVEL_SUBVOL_MOUNT_POINT={toplevel} commit_and_push_and_checkout \
			--SUBVOLUME={data}/{subvol}/ --REMOTE_SUBVOLUME=/{target_path}/{hostname}_backup/{subvol}""")


if __name__ == "__main__":
	fire.Fire(run)
