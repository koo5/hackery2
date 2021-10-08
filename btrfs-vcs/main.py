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



def run(VOL='/', HOSTNAME=None, SNAPSHOTS_CONTAINER=None, TAG=None, SNAPSHOT=None):

	VOL = Path(VOL).absolute()

	if SNAPSHOT is not None:

		SNAPSHOT = Path(SNAPSHOT).absolute()
	else:

		if HOSTNAME is None:
			HOSTNAME = subprocess.check_output(['hostname'], text=True).strip()
	
		if SNAPSHOTS_CONTAINER is None:
			SNAPSHOTS_CONTAINER = Path(str(VOL.parent) + '/.bcvs_snapshots.' + VOL.parts[-1]).absolute()
		else:
			SNAPSHOTS_CONTAINER = SNAPSHOTS_CONTAINER.absolute()

		if TAG is None:
			TAG = 'from_' + HOSTNAME

		tss = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
		#tss = subprocess.check_output(['date', '-u', "+%Y-%m-%d_%H-%M-%S"], text=True).strip()
		ts = sanitize_filename(tss.replace(' ', '_'))

		SNAPSHOT = Path(str(SNAPSHOTS_CONTAINER) + '/' + TAG + '/' + ts)

	SNAPSHOT_PARENT = os.path.split(str(SNAPSHOT))[0]
	cmd(f'mkdir -p {SNAPSHOT_PARENT}')

	cmd(f'btrfs subvolume snapshot -r {VOL} {SNAPSHOT}')

def cmd(s):
	print(s)
	os.system(s)


if __name__ == '__main__':
        fire.Fire(run)

