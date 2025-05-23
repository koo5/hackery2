#!/usr/bin/env python3

from infra import *


def run(local=False, target_path='/bac4/'):
	if local:
		ccs('sudo swipl -s /home/koom/hackery2/src/hackery2/bin/disks.pl  -g "start"')


	srun('snap list | sudo tee /root/snap_list')
	srun('ubuntu_selected_packages list | sudo tee /root/apt_list')
	srun('sudo rsync -v -a -S -v --progress -r --delete /home /root /etc /var/www /var/lib/docker/volumes /var/lib/snapd      /d2/backup/jj_ext')

	if local:
		sshstr = ''
	else:
		ip = r64_ip()
		sshstr = f'--sshstr="hpnssh  -p 44  -o TCPRcvBufPoll=yes -o NoneSwitch=yes  -o NoneEnabled=yes  koom@{ip}"'
		sshstr = f'--sshstr="ssh  -p 44  koom@{ip}"'

	for subvol in ['u','backup','images','images2']:
		ccs(f"""bfg --YES=true {sshstr} --LOCAL_FS_TOP_LEVEL_SUBVOL_MOUNT_POINT=/d2 commit_and_push_and_checkout  --SUBVOLUME=/d2/{subvol}/ --REMOTE_SUBVOLUME=/{target_path}/jj_backup/{subvol}""")


if __name__ == "__main__":
	fire.Fire(run)
