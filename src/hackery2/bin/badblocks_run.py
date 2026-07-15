#!/usr/bin/env python3
"""Run badblocks against a disk, logging into /root/bb/<timestamp>_<name>/.

	badblocks_run.py /dev/disk/by-id/usb-SABRENT_... -- -b 65536 -s -vvw

Everything after -- is passed to badblocks verbatim, as options only: the
device and the block range are ours, because badblocks wants them in the
middle of its own arg list (`badblocks [options] device [last [first]]`).
Omit --last and badblocks tests the whole disk, which is what you want.

Produces /root/bb/<ts>_<name>/:
	badblocks.log    full output (stdout+stderr), also streamed to the terminal
	badblocks.list   the bad block list (badblocks -o); feed to mke2fs -l / fsck -l
	info.txt         device identity, command line, result

A destructive pass over a large disk runs for days — start it under tmux/screen.
"""

import argparse
import datetime
import os
import re
import shlex
import stat
import subprocess
import sys

BY_ID = '/dev/disk/by-id'

# badblocks options that take a following value; needed so that peeking at the
# passthrough args doesn't mistake a value for a bundled flag.
OPTS_WITH_VALUE = {'-b', '-c', '-d', '-e', '-i', '-o', '-p', '-t'}

# badblocks stores block numbers in a 32-bit blk_t, so a whole-disk run only
# fits if size/blocksize stays under this. That, not speed, is why big disks
# need -b 65536: at the default -b 1024 an 8 TB disk needs 7.8e9 blocks and
# badblocks bails with "Value too large for defined data type".
MAX_BLOCK = 2 ** 32 - 1
DEFAULT_BLOCK_SIZE = 1024


def die(msg):
	print('badblocks_run: %s' % msg, file=sys.stderr)
	sys.exit(1)


def human(size):
	"""Byte count in the decimal units drives are actually labelled with."""
	value = float(size)
	for unit in ('B', 'kB', 'MB', 'GB', 'TB'):
		if value < 1000 or unit == 'TB':
			return '%.1f %s' % (value, unit)
		value /= 1000


def device_aliases(device):
	"""All /dev/disk/by-id names pointing at this device."""
	if not os.path.isdir(BY_ID):
		return []
	return sorted(entry for entry in os.listdir(BY_ID)
	              if os.path.realpath(os.path.join(BY_ID, entry)) == device)


def run_name(device, aliases):
	"""Name the run after the most descriptive stable alias.

	realpath() gives us 'sde', which is exactly the name that shuffles between
	boots, so prefer a by-id alias carrying model+serial. Order matters: ata-
	and friends carry the *drive's* serial, while usb- carries the enclosure
	bridge's, which is often a generic value shared by identical enclosures.
	wwn- is stable but opaque, so it's the last resort.
	"""
	for prefix in ('nvme-', 'ata-', 'scsi-', 'usb-', 'wwn-'):
		matches = [a for a in aliases if a.startswith(prefix)]
		if matches:
			name = max(matches, key=len)
			break
	else:
		name = os.path.basename(device)
	return re.sub(r'[^A-Za-z0-9._-]', '_', name)


def has_flag(tail, letter):
	"""Whether a bare flag is set, including bundled forms like -svvw.

	Values are skipped so that e.g. `-i wordlist` isn't read as a -w.
	"""
	skip = False
	for arg in tail:
		if skip:
			skip = False
		elif arg in OPTS_WITH_VALUE:
			skip = True
		elif arg.startswith('-') and letter in arg.lstrip('-'):
			return True
	return False


def block_size(tail):
	"""The -b value out of the passthrough args, or badblocks' own default.

	Peeked at purely to validate the block range up front; the tail itself is
	still handed to badblocks untouched.
	"""
	for i, arg in enumerate(tail):
		if arg == '-b' and i + 1 < len(tail):
			return int(tail[i + 1])
		bundled = re.fullmatch(r'-b(\d+)', arg)
		if bundled:
			return int(bundled.group(1))
	return DEFAULT_BLOCK_SIZE


def check_block_range(device, size, bs, last):
	"""Fail before the confirmation prompt rather than after badblocks starts."""
	on_disk = size // bs - 1
	if last > on_disk:
		die('--last %d overshoots %s: it holds %d blocks of %dB (max --last %d).\n'
		    'A 512B sector count from `blockdev --getsz` by any chance?'
		    % (last, device, on_disk + 1, bs, on_disk))
	if last > MAX_BLOCK:
		wanted = DEFAULT_BLOCK_SIZE
		while size // wanted - 1 > MAX_BLOCK:
			wanted *= 2
		die('%s needs %d blocks of %dB, but badblocks block numbers are 32-bit '
		    '(max %d).\nPass -b %d or larger — -b 65536 is the usual choice.'
		    % (device, last + 1, bs, MAX_BLOCK, wanted))


def device_state(device):
	"""Inspect the device and its children: (blockers, notes).

	blockers are reasons to refuse outright; notes are things worth putting in
	front of the human before they confirm.

	Uses lsblk's -P pairs output rather than -r: raw output separates empty
	fields with plain spaces, so a row like `zram0 disk  [SWAP]` would shift
	the mountpoint into the fstype column.
	"""
	out = subprocess.run(['lsblk', '-Pno', 'NAME,TYPE,FSTYPE,MOUNTPOINT', device],
	                     capture_output=True, text=True).stdout
	blockers, notes = [], []
	for line in out.splitlines():
		row = dict(field.split('=', 1) for field in shlex.split(line))
		name = row.get('NAME', '?')
		kind, fstype, mount = row.get('TYPE', ''), row.get('FSTYPE', ''), row.get('MOUNTPOINT', '')
		if mount:
			blockers.append('%s is mounted at %s' % (name, mount))
		if kind in ('crypt', 'raid', 'lvm'):
			# An unlocked LUKS container has no mountpoint of its own, so the
			# open dm mapping is the only thing that gives it away.
			blockers.append('%s is an open %s mapping' % (name, kind))
		if fstype == 'crypto_LUKS':
			notes.append('%s holds a LUKS header — the keyslots are '
			             'irreplaceable, and the data goes with them' % name)
	return blockers, notes


def main():
	argv = sys.argv[1:]
	if '--' in argv:
		split = argv.index('--')
		ours, tail = argv[:split], argv[split + 1:]
	else:
		ours, tail = argv, []

	parser = argparse.ArgumentParser(
		description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument('device', help='any alias: /dev/sde, /dev/disk/by-id/..., ...')
	parser.add_argument('--last', help='last block to test (default: whole disk)')
	parser.add_argument('--first', help='first block to test')
	parser.add_argument('--name', help='override the derived run name')
	parser.add_argument('--dir', default='/root/bb', help='log root (default: %(default)s)')
	parser.add_argument('--yes', action='store_true', help='skip the confirmation')
	parser.add_argument('--dry-run', action='store_true', help='print the command and stop')
	args = parser.parse_args(ours)

	if os.geteuid() != 0:
		die('must run as root')

	device = os.path.realpath(args.device)
	if not os.path.exists(device):
		die('no such device: %s' % args.device)
	if not stat.S_ISBLK(os.stat(device).st_mode):
		die('not a block device: %s (%s)' % (device, args.device))

	# -w overwrites everything. -n is only "non-destructive" if it finishes: it
	# rewrites each block and puts the original back, so an interrupted run (or
	# a block that fails the write-back) loses whatever was there. Treat both as
	# writes. A read-only pass is the only one that can't cost anything, and
	# it's fine over a mounted disk — that's what badblocks is for.
	destructive = has_flag(tail, 'w')
	writes = destructive or has_flag(tail, 'n')

	blockers, luks = device_state(device)
	if writes and blockers:
		die('%s is in use:\n  %s' % (device, '\n  '.join(blockers)))

	aliases = device_aliases(device)
	name = args.name or run_name(device, aliases)
	size = int(subprocess.run(['blockdev', '--getsize64', device],
	                          capture_output=True, text=True, check=True).stdout)

	bs = block_size(tail)
	last = int(args.last) if args.last else size // bs - 1
	check_block_range(device, size, bs, last)

	timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
	run_id = '%s_%s' % (timestamp, name)
	run_dir = os.path.join(args.dir, run_id)
	log_path = os.path.join(run_dir, 'badblocks.log')
	list_path = os.path.join(run_dir, 'badblocks.list')
	info_path = os.path.join(run_dir, 'info.txt')

	# -o writes the bad block list, tee writes the verbose log — separate files,
	# or they clobber each other.
	cmd = ['badblocks'] + tail + ['-o', list_path, device]
	if args.last:
		cmd.append(args.last)
		if args.first:
			cmd.append(args.first)
	elif args.first:
		die('--first needs --last (badblocks takes them in that order)')

	info = [
		'run          : %s' % run_id,
		'requested    : %s' % args.device,
		'device       : %s' % device,
		'aliases      : %s' % (', '.join(aliases) or '(none)'),
		'size         : %d bytes (%s)' % (size, human(size)),
		'blocks       : %d x %dB (last block %d)' % (last + 1, bs, last),
		'mode         : %s' % ('-w write test — ERASES ALL DATA' if destructive
		                       else '-n read-write test — rewrites every block in place'
		                       if writes else 'read-only test'),
		'started      : %s' % datetime.datetime.now().isoformat(timespec='seconds'),
		'command      : %s' % ' '.join(shlex.quote(c) for c in cmd),
	]
	if writes:
		for note in luks:
			info.append('WARNING      : %s' % note)
	print('\n'.join(info))

	if args.dry_run:
		print('\n--dry-run, stopping here')
		return 0

	if writes and not args.yes:
		short = os.path.basename(device)
		if destructive:
			risk = 'This -w run ERASES %s (%s).' % (device, human(size))
		else:
			risk = ('This -n run rewrites every block of %s (%s) in place.\n'
			        'It puts each block back as it goes, so anything that stops it early\n'
			        '— power, a crash, a failed write-back — takes that block with it.'
			        % (device, human(size)))
		reply = input('\n%s\nType %r to confirm: ' % (risk, short))
		if reply.strip() != short:
			die('aborted')

	os.makedirs(run_dir, exist_ok=True)
	with open(info_path, 'w') as fh:
		fh.write('\n'.join(info) + '\n')
		lsblk_cols = 'NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT,MODEL,SERIAL'
		for title, probe in (('lsblk', ['lsblk', '-o', lsblk_cols, device]),
		                     ('smartctl -a', ['smartctl', '-a', device])):
			fh.write('\n--- %s ---\n' % title)
			fh.flush()
			subprocess.run(probe, stdout=fh, stderr=subprocess.STDOUT)

	print('\nlogging to %s\n' % run_dir)

	# badblocks draws its progress meter with \r on stderr, so read raw chunks
	# rather than lines — otherwise the meter never flushes through.
	with open(log_path, 'wb') as fh:
		proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		while True:
			chunk = proc.stdout.read1(4096)
			if not chunk:
				break
			sys.stdout.buffer.write(chunk)
			sys.stdout.buffer.flush()
			fh.write(chunk)
			fh.flush()
		rc = proc.wait()

	bad = sum(1 for _ in open(list_path)) if os.path.exists(list_path) else 0
	tail_info = [
		'',
		'finished     : %s' % datetime.datetime.now().isoformat(timespec='seconds'),
		'exit code    : %d' % rc,
		'bad blocks   : %d' % bad,
	]
	print('\n'.join(tail_info))
	with open(info_path, 'a') as fh:
		fh.write('\n'.join(tail_info) + '\n')

	return rc


if __name__ == '__main__':
	sys.exit(main())
