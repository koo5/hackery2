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
import click



@click.command()
@click.option('--HOSTNAME', type=str, default=None)
@click.option('--SNAPSHOTS_CONTAINER', type=str, default=None)
@click.option('--TAG', type=str, default=None)
@click.option('--SNAPSHOT', type=str, default=None)

def run(HOSTNAME, SNAPSHOTS_CONTAINER, TAG, SNAPSHOT):

	if HOSTNAME is None:
		HOSTNAME = subprocess.check_output(['hostname'])

	VOL = Path(VOL)


	if SNAPSHOTS_CONTAINER is None:
		if VOL == '/':
			SNAPSHOTS_CONTAINER_PARENT = '/'
		else:
			
			SNAPSHOTS_CONTAINER_PARENT = VOL + '../'
		last_part_of_VOL_path = vol.parts[-1]
		SNAPSHOTS_CONTAINER = SNAPSHOTS_CONTAINER_PARENT + '.bcvs_snapshots.' + last_part_of_VOL_path
		os.system(f'mkdir -p {SNAPSHOTS_CONTAINER}')


	if TAG is None:
		TAG = 'from_' + HOSTNAME


	ts = sanitize_filename(time.asctime())


	if SNAPSHOT is None:
		SNAPSHOT = SNAPSHOTS_CONTAINER + '/' + TAG + '/' + ts


	os.system('btrfs subvolume snapshot -r {VOL} {SNAPSHOT}')



if __name__ == '__main__':
        run()

