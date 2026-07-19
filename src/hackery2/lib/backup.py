#!/usr/bin/env python3


"""
install:
 pip install click ptyprocess


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
import re
import os
import shlex # Added for splitting command output
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from .infra import *
from . import locks
import logging
import click
import json5
log = logging.getLogger()
# Set up logging
log.setLevel(logging.INFO)
if 'BACKUP_DEBUG' in os.environ:
	log.setLevel(logging.DEBUG)


_use_db = True


LOCK_DIR = '/run/lock'


_exit_if_locked = False


@click.group()
@click.option('--exit-if-locked', is_flag=True,
			  help='If another run of the same pipeline holds its lock, exit immediately '
				   '(code 75) instead of waiting. Use for cron so runs cannot pile up behind a '
				   'stuck one.')
def cli(exit_if_locked):
	"""Backup utility with three modes: snapshot-only, local backup, and remote backup."""
	global _exit_if_locked
	_exit_if_locked = exit_if_locked


def _lock_path(resource):
	slug = re.sub(r'[^A-Za-z0-9._-]+', '_', str(resource).strip('/')) or 'root'
	return f'{LOCK_DIR}/backup.py.{slug}.lock'


def _take_pipeline_lock(name):
	# Pipeline-identity locking: each pipeline mode takes locks that only prevent
	# a duplicate of itself working the same resource (cron pileup, a
	# double-started manual run) - 'snapshots', 'vpss:<target>', 'clean:<fs>'.
	# Cross-pipeline and cross-machine concurrency is
	# deliberately not serialized here; it is governed where the data lives:
	# every receive holds a .series flock on its target dir (a duplicate transfer
	# of the same series exits EX_TEMPFAIL and bfg skips it), and every deletion
	# decision runs under bfg's db advisory lock, which enforces the
	# newer-live-pair invariant. local/remote transfer runs therefore take no
	# machine lock at all. Returns the lock fd: most callers hold until process
	# exit, clean releases each fs's lock (os.close) when moving to the next.
	# Called at the start of the actual work (not in the group callback, where it
	# would also make `backup <cmd> --help` block on the lock).
	path = _lock_path(name)
	try:
		return locks.acquire(path, wait=not _exit_if_locked)
	except locks.LockHeld as e:
		print(f'{e} - another {name} run is in progress, exiting (--exit-if-locked)',
			  file=sys.stderr)
		sys.exit(75)  # EX_TEMPFAIL: "transient, try again later" for cron

@cli.command()
@click.option('--source', default='host', help='Source to backup')
@click.option('--quick', is_flag=True, help='Quick mode - skip some operations')
@click.option('--prune/--no-prune', default=True, help='Prune old snapshots')
def snapshot(source, quick, prune):
	"""Mode 1: Create local snapshots only (no backup target needed)."""
	print(f'Creating snapshots only - source={source}, quick={quick}, prune={prune}')
	_run_backup(source=source, target_machine=None, target_fs=None, local=True, quick=quick, prune=prune, snapshot_only=True)

@cli.command()
@click.option('--source', default='host', help='Source to backup')
@click.option('--target-fs', required=True, help='Target filesystem for local backup')
@click.option('--quick', is_flag=True, help='Quick mode - skip some operations')
@click.option('--prune/--no-prune', default=True, help='Prune old backups')
def local(source, target_fs, quick, prune):
	"""Mode 2: Create backups to a local backup location."""
	print(f'Local backup - source={source}, target_fs={target_fs}, quick={quick}, prune={prune}')
	_run_backup(source=source, target_machine=None, target_fs=target_fs, local=True, quick=quick, prune=prune, snapshot_only=False)

@cli.command()
@click.option('--source', default='host', help='Source to backup')
@click.option('--target-fs', required=True, help='Target filesystem for local backup')
@click.option('--quick', is_flag=True, help='Quick mode - skip some operations')
@click.option('--prune/--no-prune', default=True, help='Prune old backups')
def vpss(source, target_fs, quick, prune):
	_run_backup(source=source, target_machine=None, target_fs=target_fs, local=True, quick=quick, prune=prune, snapshot_only=False, vpss=True)

@cli.command()
@click.option('--source', default='host', help='Source to backup')
@click.option('--percent', default=30.0, type=float, help='Percentage of oldest snapshots to clean (default 30)')
@click.option('--min-free', default=None,
			  help='Instead of percent-of-series, delete oldest unprotected snapshots fs-wide only '
				   'until this much space is free (e.g. 500G, 2T). Idempotent - safe to re-run/cron.')
@click.option('--dry-run', is_flag=True, help='Only report what would be cleaned, delete nothing')
def clean(source, percent, min_free, dry_run):
	"""Aggressively clean old local snapshots, keeping only those needed as shared parents for future incremental sends."""
	print(f'Clean old snapshots - source={source}, percent={percent}, min_free={min_free}, dry_run={dry_run}')
	_run_clean(source=source, percent=percent, min_free=min_free, dry_run=dry_run)

@cli.command()
@click.option('--source', default='host', help='Source to backup')
@click.option('--percent', default=30.0, type=float, help='Clean percentage to simulate (default 30)')
@click.option('--all', 'show_all', is_flag=True, help='List every snapshot instead of collapsing the trivially-kept recent ones')
def report(source, percent, show_all):
	"""Read-only: show a per-subvol table of local snapshots and what prune+clean would do to each (and which ones are held as shared parents)."""
	print(f'Snapshot report - source={source}, percent={percent}, all={show_all}')
	_run_report(source=source, percent=percent, show_all=show_all)

@cli.command()
@click.option('--source', default='host', help='Source to backup')
@click.option('--target-machine', required=True, help='Remote machine for backup (e.g., r64, jj)')
@click.option('--target-fs', help='Target filesystem on remote machine')
@click.option('--quick', is_flag=True, help='Quick mode - skip some operations')
@click.option('--prune/--no-prune', default=True, help='Prune old backups')
@click.option('--backups/--no-backups', default=False, help='Also transfer all most recent snapshots in backups to remote machine')
def remote(source, target_machine, target_fs, quick, prune, backups):
	"""Mode 3: Create backups to a remote machine."""
	print(f'Remote backup - source={source}, target_machine={target_machine}, target_fs={target_fs}, quick={quick}, prune={prune}')
	_run_backup(source=source, target_machine=target_machine, target_fs=target_fs, local=False, quick=quick, prune=prune, snapshot_only=False)



def _run_backup(source='host', target_machine=None, target_fs=None, local=False, quick=False, prune=True, snapshot_only=False, vpss=False, backups=False):

	print(f'_run_backup: source = {source}, target_machine = {target_machine}, target_fs = {target_fs}, local = {local}, quick = {quick}, prune = {prune}, snapshot_only = {snapshot_only}')

	default_target_machine = 'jj'
	default_target_fs='/bac20/'

	if hostname == 'r64':
		default_target_machine = None
		default_target_fs = '/bac19/'

	if target_machine is None:
		target_machine = default_target_machine
	if target_fs is None:
		target_fs = default_target_fs

	if target_machine == 'None':
		print('target_machine = None')
		target_machine = None

	if snapshot_only:
		_take_pipeline_lock('snapshots')
	elif vpss:
		# the vps rsync phase is not series-guarded, so two vpss runs into the SAME
		# target must serialize (interleaved rsync --delete into the same dirs);
		# vpss runs into different target disks are useful concurrency and proceed
		_take_pipeline_lock(f'vpss:{target_fs}')
	# local/remote transfer runs take no machine lock, see _take_pipeline_lock

	if not local:
		print(f'target_machine = {target_machine}')
		sshstr, sshstr2 = set_up_target(target_machine, quick)
	else:
		sshstr = ''
		sshstr2 = ''

	if not local:
		check_if_mounted(sshstr, target_fs)

	fss = get_filesystems()
	
	if hostname != 'r64':
		sync_stuff(hostname)

	if vpss:
		backup_vpss(target_fs)
	else:
		# grab whatever info would not be transferred from ext4 partitions
		#srun('sudo snap save')
		srun('snap list | sudo tee /root/snap_list')
		srun('ubuntu_selected_packages list | sudo tee /root/apt_list')
		# anything else?
		# pause firefox? pause some vms?

	import_noncows(source, hostname, target_fs, fss)

	print()
	print('---done import_noncows---')
	print()
	if backups:
		fss[-1]['subvols'].extend(find_backup_subvols(fss[-1]))
	print()
	print('---done find_backup_subvols---')
	print()
	transfer_btrfs_subvolumes(sshstr, sshstr2, fss, target_fs, local, prune, snapshot_only)


def _run_clean(source='host', percent=30.0, min_free=None, dry_run=False):
	"""
	Aggressively clean old local snapshots on this machine's source filesystems.

	Mirrors the subvol iteration of the local prune step, but calls bfg clean_local, which
	deletes the oldest `percent`% of snapshots while refusing to delete snapshots that are
	still needed as shared parents for future incremental sends.

	With min_free set, cleaning is goal-based instead: after the usual prune, each
	filesystem gets bfg clean_fs --MIN_FREE, which deletes oldest unprotected snapshots
	fs-wide only until that much space is free (idempotent, so re-running compounds nothing).
	"""
	print(f'_run_clean: source = {source}, percent = {percent}, min_free = {min_free}, dry_run = {dry_run}')

	fss = get_filesystems()
	mounted = [fs for fs in fss if check_if_mounted_local(fs['toplevel'])]
	for fs in fss:
		if fs not in mounted:
			print('SKIP non-mounted ' + fs['toplevel'])

	# first refresh the db for ALL local filesystems, so that both directions of
	# shared-snapshot detection (source-side prune protecting pairs on the targets, and
	# target-side pile cleaning protecting pairs with the sources) see current state -
	# not the state from whenever the last backup or manual update_db happened to run.
	if _use_db:
		for fs in mounted:
			ccs(f"""bfg --YES=true update_db --FS={fs['toplevel']} """)

	for fs in mounted:
		toplevel = fs['toplevel']

		dry = ' --DRY_RUN=True' if dry_run else ''

		# cleans of the same fs serialize; cleans of different fss (e.g. two piles on
		# separate disks) run concurrently. Deliberately NOT serialized against
		# transfers: min-free clean maintains a free-space floor and is meant to run
		# while backups land - evicting the oldest unprotected tail to make room for
		# incoming data is its job. Released per fs so an overlapping clean run can
		# pipeline through the remaining disks behind this one.
		lock_fd = _take_pipeline_lock(f'clean:{toplevel}')
		try:
			if fs.get('transfer_only'):
				# backup-target filesystem: holds piles of received snapshots with no origin
				# subvolume here, so prune/clean them per series (fs-wide), protecting the
				# shared pairs found via the db.
				print('PRUNE FS ' + toplevel)
				ccs(f"""bfg prune_fs --DB={_use_db} --YES=true{dry} --FS={toplevel} """)
				print('CLEAN FS ' + toplevel)
				if min_free:
					ccs(f"""bfg clean_fs --DB={_use_db} --YES=true --MIN_FREE={min_free}{dry} --FS={toplevel} """)
				else:
					ccs(f"""bfg clean_fs --DB={_use_db} --YES=true --PERCENT={percent}{dry} --FS={toplevel} """)
				continue

			for subvol in fs['subvols']:
				if subvol.get('just_push'):
					continue
				name = subvol['name']
				source_path = subvol['source_path']
				subvol_path = Path(f"{toplevel}/{source_path}{name}")
				# first thin the history with the normal time-based retention policy, then
				# (below) aggressively drop old snapshots.
				print('PRUNE ' + str(subvol_path))
				ccs(f"""bfg prune_local --DB={_use_db} --YES=true{dry} --SUBVOL={subvol_path} """)
				if not min_free:
					print('CLEAN ' + str(subvol_path))
					ccs(f"""bfg clean_local --DB={_use_db} --YES=true --PERCENT={percent}{dry} --SUBVOL={subvol_path} """)

			if min_free:
				# goal-based cleaning covers the whole fs at once (series discovery also
				# finds the flat local snapshot layout)
				print('CLEAN FS ' + toplevel)
				ccs(f"""bfg clean_fs --DB={_use_db} --YES=true --MIN_FREE={min_free}{dry} --FS={toplevel} """)
		finally:
			os.close(lock_fd)


def _run_report(source='host', percent=30.0, show_all=False):
	"""
	Read-only report: for each source subvol on this machine, refresh the db and print the
	prune+clean plan (what would be kept/removed and why) via bfg report_local. Deletes nothing.
	"""
	print(f'_run_report: source = {source}, percent = {percent}, all = {show_all}')

	# no lock: read-only wrt subvols (update_db serializes itself via bfg's db
	# advisory lock), and a report must be runnable while a long backup is in flight

	fss = get_filesystems()

	all_flag = ' --ALL=True' if show_all else ''

	mounted = [fs for fs in fss if check_if_mounted_local(fs['toplevel'])]
	for fs in fss:
		if fs not in mounted:
			print('SKIP non-mounted ' + fs['toplevel'])

	# refresh the db for ALL local filesystems first (see _run_clean for why)
	if _use_db:
		for fs in mounted:
			ccs(f"""bfg --YES=true update_db --FS={fs['toplevel']} """)

	for fs in mounted:
		toplevel = fs['toplevel']

		if fs.get('transfer_only'):
			ccs(f"""bfg report_fs --DB={_use_db} --PERCENT={percent}{all_flag} --FS={toplevel} """)
			continue

		for subvol in fs['subvols']:
			if subvol.get('just_push'):
				continue
			name = subvol['name']
			source_path = subvol['source_path']
			subvol_path = Path(f"{toplevel}/{source_path}{name}")
			ccs(f"""bfg report_local --DB={_use_db} --PERCENT={percent}{all_flag} --SUBVOL={subvol_path} """)


def sync_stuff(hostname):
	where = f'/d/sync/jj/host/{hostname}/'
	what = f'/home/koom/.local/share/fish/fish_history'
	cc(ss(f'mkdir -p {where}'))
	srun(f'rsync --one-file-system -v -a -S -v --progress -r --delete {what} {where}')


def import_noncows(source, hostname, target_fs, fss):
	"""
	todo: we should make a snapshot of each subvol right after the transfer is finished. This will parallel how btrfs snapshots are "imported".
	"""
	rsync_ext4_filesystems_into_backup_folder(fss)


def set_up_target(target_machine, quick):

	if target_machine is None:
		#if not quick:
		#	ccs('sudo swipl -s /home/koom/hackery2/src/hackery2/bin/disks.pl  -g "start"')
		return  '', ''

	insecure_speedups = ''
	ssh = get_hpnssh_executable()

	if target_machine == 'r64.internal':
		#insecure_speedups = '-o NoneSwitch=yes  -o NoneEnabled=yes'
		long_ssh = ' -o ServerAliveInterval=600 -o ServerAliveCountMax=999999  -o TCPKeepAlive=no  '
		sshstr = f'{ssh}  -p 2222  -o TCPRcvBufPoll=yes {long_ssh} {insecure_speedups} koom@r64.internal'

	if target_machine == 'jj.internal':
		#insecure_speedups = '-o NoneSwitch=yes  -o NoneEnabled=yes'
		long_ssh = ' -o ServerAliveInterval=600 -o ServerAliveCountMax=999999  -o TCPKeepAlive=no  '
		sshstr = f'{ssh}  -p 2222  -o TCPRcvBufPoll=yes {long_ssh} {insecure_speedups} koom@jj.internal'


	elif target_machine == 'jj':
		long_ssh = ' -o ServerAliveInterval=600 -o ServerAliveCountMax=999999  -o TCPKeepAlive=no  '
		sshstr = f'{ssh}  -p 2222  -o TCPRcvBufPoll=yes {long_ssh} {insecure_speedups} koom@10.0.0.24'


	elif target_machine == 'r64':
		r64_ip = get_r64_ip()
		#if r64_ip.startswith('10.'):
		#	insecure_speedups = '-o NoneSwitch=yes  -o NoneEnabled=yes'
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
				'toplevel': '/bac20',
				'subvols': m(['cold']),
				'transfer_only': True
			},
			{
				'toplevel': '/d2',
				'subvols': m(['u/sync', 'u', 'dev3', 'home', '/', 'images/dev4']),
			},
		]
	elif hostname == 'r64':
		fss = [
		{
			'snapshot_only': True,
			'toplevel': '/home/koom/Sync',
			'subvols': m(['/'])
		},
		{
			'toplevel': '/',
			'subvols': m(['/']),
		},
		]
	elif hostname == 't14':
		fss = [{
			'toplevel': '/',
			'subvols': m(['/'])
		},
		{
			'toplevel': '/data',
			'subvols': m(['/', {'path': 'data/sync', 'snapshot_only': True}]),
		}]
	return fss


def transfer_btrfs_subvolumes(sshstr, sshstr2, fss, target_fs, local, prune, snapshot_only=False):
	for fs in fss:
		if fs.get('snapshot_only') and not snapshot_only:
			continue
		if fs.get('transfer_only', False) and snapshot_only:
			continue
		if not check_if_mounted_local(fs['toplevel']):
			print('SKIP non-mounted ' + fs['toplevel'])
			continue
		if local and Path(fs['toplevel']) == Path(target_fs):
			print('SKIP local ' + fs['toplevel'])
			continue
		toplevel = fs['toplevel']
		for subvol in fs['subvols']:
			if not snapshot_only and subvol.get('snapshot_only'):
				continue
			if subvol.get('just_push'):
				if not local:
					print('PUSH ' + toplevel + '/' + subvol['path'])
					subvol_path = Path(toplevel)/subvol['path']
					remote_subvol_path = Path(target_fs)/subvol['path']
					ccs(f"""bfg --YES=true {sshstr2} push --SUBVOL={subvol_path} --REMOTE_SUBVOL={remote_subvol_path} """)
				continue
			name = subvol['name']
			print('BACKUP ' + toplevel + '/' + name)
			source_path = subvol['source_path']
			target_dir = subvol['target_dir']
			target_subvol_name = name if name != '/' else toplevel.replace('/', '_') + '_root'
			subvol_path = Path(f"{toplevel}/{source_path}{name}")
			#ccs(f"""date""")
			if snapshot_only:
				# Mode 1: Only create local snapshots
				ccs(f"""bfg --YES=true local_commit --SUBVOL={subvol_path} """)
			elif local:
				# Mode 2: Local backup
				remote_subvol_path = Path(target_fs)/'backups'/target_dir/target_subvol_name
				ccs(f"""bfg --YES=true commit_and_push --SUBVOL={subvol_path} --REMOTE_SUBVOL={remote_subvol_path} """)
			else:
				# Mode 3: Remote backup
				remote_subvol_path = Path(target_fs)/'backups'/target_dir/target_subvol_name
				ccs(f"""bfg --YES=true {sshstr2} commit_and_push --SUBVOL={subvol_path} --REMOTE_SUBVOL={remote_subvol_path} """)
			#ccs(f"""date""")
			print('', file = sys.stderr)
		if _use_db:
			ccs(f"""bfg --YES=true update_db --FS={toplevel} """)
			# also rescan the target fs, so that the prune below sees the snapshots we just
			# pushed and protects the shared pairs - otherwise the source-side prune keeps
			# deleting the very snapshots that future incremental sends need as parents.
			if not snapshot_only:
				if local:
					ccs(f"""bfg --YES=true update_db --FS={target_fs} """)
				else:
					ccs(f"""{sshstr} bfg --YES=true --FS={target_fs} update_db """)

		#ccs(f"""bfg prune_stashes --YES=true --FS={target_fs} """)

		if prune:
			for subvol in fs['subvols']:
				if subvol.get('just_push'):
					# todo pruning
					continue
				log.debug(f'pruning {subvol=}')
				name = subvol['name']
				source_path = subvol['source_path']
				target_dir = subvol['target_dir']
				target_subvol_name = name if name != '/' else toplevel.replace('/', '_') + '_root'
				subvol_path = Path(f"{toplevel}/{source_path}{name}")
				ccs(f"""bfg prune_local --DB={_use_db} --YES=true  --SUBVOL={subvol_path} """)
				if not local and not snapshot_only:
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
	# this path corresponds to the structure expected by find_backup_subvols and also created by transfer_btrfs_subvolumes, that is, /mountpoint/backups/hostname/subvol
	where = f"{fss[-1]['toplevel']}/backups/{hostname}/{name}"
	if not Path(where).exists():
		ccs(f'sudo btrfs sub create {where}')
	# todo figure out how to tell rsync not to try to sync what it can't sync, and then we can start checking its results
	srun(f'sudo rsync --one-file-system -v -a -S -v --progress -r --delete {what} {where}')



import getpass
import os
import grp




def backup_vpss(target_fs):
	with open(os.path.expanduser('/d/sync/jj/secrets.json'), 'r') as f:
		for cloud_host in json5.load(f)['vpss']:
			if isinstance(cloud_host, dict):
				# New schema with filesystem specifications
				backup_vps_with_fs(target_fs, cloud_host)
			else:
				# Legacy string format
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


def backup_vps_with_fs(target_fs, host_config):
	"""Backup VPS with filesystem specifications using bfg remote_commit_and_pull."""
	host = host_config['host']
	fss = host_config['fss']
	
	log.info(f"Backing up {host} with {len(fss)} filesystems")
	
	# Set up SSH connection for remote bfg operations
	ssh = get_hpnssh_executable()
	sshstr = f'{ssh} root@{host}'
	sshstr2 = '--sshstr="' + sshstr + '"'
	
	for fs in fss:
		toplevel = fs['toplevel']
		subvols = fs['subvols']
		
		for subvol in subvols:
			# Construct paths
			remote_subvol = Path(toplevel) / subvol if subvol != '/' else Path(toplevel)
			subvol_name = subvol if subvol != '/' else toplevel.replace('/', '_') + '_root'
			local_backup_path = Path(target_fs) / 'backups' / host / subvol_name
			
			log.info(f"Remote commit and pull: {remote_subvol} -> {local_backup_path}")
			
			try:
				# Use bfg's remote_commit_and_pull command
				ccs(f"bfg --YES=true {sshstr2} remote_commit_and_pull {remote_subvol} {local_backup_path}")
				
			except Exception as e:
				log.error(f"Failed to backup {remote_subvol} from {host}: {e}")
				# Continue with other subvolumes even if one fails
				continue


def parse_snapshot_name(dname):
	# Typical pattern might be:
	#   <subvol>_bfg_snapshots_<timestamp>_<tag>
	#   <subvol>_<timestamp>_<tag>
	# We'll attempt to capture all via two regex tries:

	m = re.match(r'(.+)_bfg_snapshots_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})_(.*)', dname)
	if m is None:
		m = re.match(r'(.+)_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})_(.*)', dname)
	if m is None:
		raise Exception(f'could not parse snapshot folder: {dname}')
	return (
		{'name': m.group(1),
		 'dt': datetime.strptime(m.group(2), "%Y-%m-%d_%H-%M-%S"),
		 'tags': m.group(3)}) # type: ignore


def find_backup_subvols(fs):
	"""
	Walks the backup directory structure for a given filesystem `fs` to find
	the latest snapshot for each backed-up subvolume.

	Uses `btrfs subvolume list` to find snapshots within the backup structure.
	The expected path structure relative to the filesystem root is:
	backups/<host>/<original_subvol_path>/.bfg_snapshots/<snapshot_name>
	"""
	toplevel = fs['toplevel']
	print(f'Looking for backup snapshots using btrfs subvolume list on: {toplevel}')

	latest_snapshots = defaultdict(lambda: {'dt': datetime.min, 'path': None, 'rel_path': None})

	try:
		# Execute the btrfs command
		cmd = f"sudo btrfs subvolume list -q -t -R -u -a {toplevel}"
		output = co(shlex.split(cmd))
	except Exception as e:
		log.error(f"Failed to execute btrfs command: {cmd}\nError: {e}")
		sys.exit(1)

	lines = output.strip().split('\n')
	if len(lines) <= 2:
		print("No subvolume information found or only header present.")
		return []

	# Skip header lines (first 2)
	for line in lines[2:]:
		try:
			parts = line.split()
			if len(parts) < 7:
				log.warning(f"malformed line: {line}")
				sys.exit(1)

			# 7th column (index 6) is the relative path
			rel_path_str = parts[6]
			path_parts = Path(rel_path_str).parts

			# Check structure: backups/<host>/.../.bfg_snapshots/<snapshot_name>
			if len(path_parts) >= 4 and path_parts[0] == 'backups' and path_parts[-2] == '.bfg_snapshots':
				original_subvol_parts = path_parts[1:]
				print(f'original_subvol_parts: {original_subvol_parts}')
				original_subvol_rel_path = os.path.join(*original_subvol_parts)
				snapshot_name = path_parts[-1]

				try:
					parsed = parse_snapshot_name(snapshot_name)
					name = parsed['name']
					key = os.path.join(os.path.join(*original_subvol_parts[:-1]), name)
					if parsed['dt'] > latest_snapshots[key]['dt']:
						# Store both relative and absolute path for potential use
						absolute_path = Path(toplevel) / rel_path_str
						latest_snapshots[key] = {'dt': parsed['dt'], 'path': absolute_path, 'rel_path': rel_path_str}
				except Exception as e:
					log.debug(f"Could not parse potential snapshot name '{snapshot_name}' from path '{rel_path_str}': {e}")

		except Exception as e:
			log.warning(f"Error processing line: {line}\nError: {e}")


	if latest_snapshots:
		print('Found latest snapshots:')
		for key, data in latest_snapshots.items():
			print(f"  Key: {key}, Latest: {data['dt']}, Rel: {data['rel_path']}")
	else:
		print("  No snapshots found.")

	return [{
		'just_push': True,
		'path': data['rel_path']
	}]




def m(subvols):
	"""return subvol specifications for a machine's filesystem"""
	return [{'target_dir': hostname,
			'name': subvol if isinstance(subvol, str) else subvol['path'],
			'source_path':'',
			 'snapshot_only': isinstance(subvol, dict) and subvol.get('snapshot_only', False)
			 } for subvol in subvols]


def check_if_mounted_local(fs):
	for line in co(shlex.split('cat /etc/mtab')).strip().split('\n'):
		items = line.split()
		if items[1] == fs or items[1] + '/' == fs:
			return True


def check_if_mounted(sshstr, target_fs):
	for line in co(shlex.split(f'{sshstr} -t "cat /etc/mtab"')).strip().split('\n'):
		print(line)
		items = line.split()
		if items[1] == target_fs or items[1] + '/' == target_fs:
			return
	raise Exception(f'{target_fs} not mounted')



if __name__ == "__main__":
	if _use_db:
		if subprocess.call(['bash', '-c', """PGPASSWORD='bfg' psql -h hours.internal -U bfg -d bfg -1 -c "select from snapshots" --echo-all"""], stdout=subprocess.PIPE) != 0:
			sys.exit(1)
	cli()



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
