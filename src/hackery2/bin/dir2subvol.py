#!/usr/bin/env python3
"""Convert a directory on btrfs into a subvolume, in place, without losing nodatacow.

	dir2subvol.py ~/.android
	dir2subvol.py --dry-run ~/.android
	dir2subvol.py --delete-old ~/.android

Btrfs has no "turn this directory into a subvolume" operation. The usual dance is
mv-aside, `btrfs subvolume create`, `cp -a --reflink`, verify, delete the old copy.
The trap is the nodatacow flag (chattr +C): no copy tool preserves it, and btrfs
refuses to reflink between a nodatacow file and a normal one, so an emulator or VM
image directory either fails to clone or silently loses the flag. This script
replicates the flag on the destination *before* cloning, because +C only sticks on
empty files and is inherited from the parent directory.

Steps:
	1. sanity checks: on btrfs, not a mountpoint, not already a subvolume,
		no nested subvolumes, nothing has files under it open
	2. rename DIR -> DIR.dir2subvol-old
	3. btrfs subvolume create DIR
	4. pre-create every directory/file whose nodatacow state differs from what it
		would inherit, with the right flag
	5. cp -a --reflink=always OLD/. DIR/   (always: a flag mismatch fails loudly
		instead of silently eating disk with a full copy)
	6. verify: same entries, sizes and nodatacow flags on both sides
	7. keep the old copy unless --delete-old; both share extents, so it costs
		nothing until the images start being written to

Run with sudo when the tree is not entirely yours, or when the open-file check
cannot see other users' processes.
"""

import argparse
import fcntl
import os
import shutil
import stat
import struct
import subprocess
import sys

# linux/fs.h: FS_IOC_GETFLAGS = _IOR('f', 1, long), FS_IOC_SETFLAGS = _IOW('f', 2, long)
_LONG = struct.calcsize('l')
FS_IOC_GETFLAGS = (2 << 30) | (_LONG << 16) | (ord('f') << 8) | 1
FS_IOC_SETFLAGS = (1 << 30) | (_LONG << 16) | (ord('f') << 8) | 2
FS_NOCOW_FL = 0x00800000

BTRFS_FIRST_FREE_OBJECTID = 256  # inode number of every subvolume root
OLD_SUFFIX = '.dir2subvol-old'


class Abort(Exception):
	pass


def say(msg):
	print(msg, flush=True)


# ---------------------------------------------------------------- inode flags

def _open_noatime(path):
	return os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)


def get_nocow(path):
	"""True/False for directories and regular files, None where flags are unsupported."""
	try:
		fd = _open_noatime(path)
	except OSError:
		return None
	try:
		raw = fcntl.ioctl(fd, FS_IOC_GETFLAGS, b'\0' * _LONG)
	except OSError:
		return None
	finally:
		os.close(fd)
	return bool(struct.unpack('l', raw)[0] & FS_NOCOW_FL)


def set_nocow(path, want):
	fd = _open_noatime(path)
	try:
		flags = struct.unpack('l', fcntl.ioctl(fd, FS_IOC_GETFLAGS, b'\0' * _LONG))[0]
		flags = (flags | FS_NOCOW_FL) if want else (flags & ~FS_NOCOW_FL)
		fcntl.ioctl(fd, FS_IOC_SETFLAGS, struct.pack('l', flags))
	finally:
		os.close(fd)
	if get_nocow(path) != want:
		# btrfs silently ignores +C/-C on non-empty files; we only ever do this on empty ones
		raise Abort(f'could not set nodatacow={want} on {path}')


# ---------------------------------------------------------------- checks

def findmnt(path):
	out = subprocess.run(
		['findmnt', '-n', '-o', 'TARGET,FSTYPE', '-T', path],
		capture_output=True, text=True, check=True).stdout.split()
	return out[0], out[1]


def is_subvolume(path):
	st = os.lstat(path)
	return stat.S_ISDIR(st.st_mode) and st.st_ino == BTRFS_FIRST_FREE_OBJECTID


def procs_using(path):
	"""Processes with an fd, cwd, exe or mapping under path. Returns (hits, unreadable_pids)."""
	prefix = path + '/'
	hits = {}
	unreadable = 0

	def under(target):
		return target == path or target.startswith(prefix)

	for pid in os.listdir('/proc'):
		if not pid.isdigit():
			continue
		proc = f'/proc/{pid}'
		try:
			found = False
			for link in ('cwd', 'exe', 'root'):
				try:
					if under(os.readlink(f'{proc}/{link}')):
						found = True
				except FileNotFoundError:
					pass
			for fd in os.listdir(f'{proc}/fd'):
				try:
					if under(os.readlink(f'{proc}/fd/{fd}')):
						found = True
				except FileNotFoundError:
					pass
			with open(f'{proc}/maps') as maps:
				for line in maps:
					parts = line.split(maxsplit=5)
					if len(parts) == 6 and under(parts[5].rstrip('\n')):
						found = True
			if found:
				with open(f'{proc}/comm') as comm:
					hits[int(pid)] = comm.read().strip()
		except PermissionError:
			unreadable += 1
		except (FileNotFoundError, ProcessLookupError):
			pass  # exited meanwhile
	return hits, unreadable


# ---------------------------------------------------------------- tree walking

def scan(root):
	"""Walk root. Returns (entries, nested_subvols).

	entries: relpath -> (kind, size, nocow); kind in 'd' 'f' 'l' 'o'; root itself is ''.
	"""
	entries = {}
	nested = []

	def record(abspath, rel):
		st = os.lstat(abspath)
		if stat.S_ISDIR(st.st_mode):
			entries[rel] = ('d', 0, get_nocow(abspath))
			if rel and st.st_ino == BTRFS_FIRST_FREE_OBJECTID:
				nested.append(rel)
		elif stat.S_ISREG(st.st_mode):
			entries[rel] = ('f', st.st_size, get_nocow(abspath))
		elif stat.S_ISLNK(st.st_mode):
			entries[rel] = ('l', 0, None)
		else:
			entries[rel] = ('o', 0, None)

	def on_error(err):
		raise Abort(f'cannot read {err.filename}: {err.strerror}')

	record(root, '')
	for dirpath, dirnames, filenames in os.walk(root, onerror=on_error):
		for name in dirnames + filenames:
			abspath = os.path.join(dirpath, name)
			record(abspath, os.path.relpath(abspath, root))
	return entries, nested


def plan_precreate(entries):
	"""Entries whose nodatacow differs from their parent's, i.e. what inheritance would
	not reproduce. Ordered parents-first. Root is always included (a fresh subvolume
	inherits nothing)."""
	todo = []
	for rel in sorted(entries, key=lambda r: (r.count('/'), r)):
		kind, _size, nocow = entries[rel]
		if kind not in ('d', 'f') or nocow is None:
			continue
		if rel == '':
			todo.append((rel, kind, nocow))
			continue
		parent = os.path.dirname(rel)
		if entries[parent][2] != nocow:
			todo.append((rel, kind, nocow))
	return todo


# ---------------------------------------------------------------- the conversion

def precreate(new_root, todo):
	for rel, kind, nocow in todo:
		target = os.path.join(new_root, rel) if rel else new_root
		if kind == 'd':
			os.makedirs(target, exist_ok=True)
		else:
			os.makedirs(os.path.dirname(target), exist_ok=True)
			os.close(os.open(target, os.O_CREAT | os.O_WRONLY | os.O_EXCL, 0o600))
		set_nocow(target, nocow)


def verify(new_root, old_entries):
	new_entries, _nested = scan(new_root)
	problems = []
	for rel, (kind, size, nocow) in old_entries.items():
		got = new_entries.get(rel)
		if got is None:
			problems.append(f'missing: {rel}')
		elif got[0] != kind:
			problems.append(f'type differs: {rel} ({kind} -> {got[0]})')
		elif kind == 'f' and got[1] != size:
			problems.append(f'size differs: {rel} ({size} -> {got[1]})')
		elif nocow is not None and got[2] != nocow:
			problems.append(f'nodatacow differs: {rel} ({nocow} -> {got[2]})')
	for rel in new_entries:
		if rel not in old_entries:
			problems.append(f'unexpected in new tree: {rel}')
	return problems


def summarize(entries):
	kinds = {'d': 0, 'f': 0, 'l': 0, 'o': 0}
	nocow = 0
	size = 0
	for kind, sz, nc in entries.values():
		kinds[kind] += 1
		size += sz
		nocow += bool(nc)
	return (f'{kinds["d"]} dirs, {kinds["f"]} files, {kinds["l"]} symlinks, '
		f'{kinds["o"]} other, {size / 2**30:.1f} GiB apparent, {nocow} entries nodatacow')


def convert(path, dry_run, force, delete_old):
	path = os.path.realpath(path)
	if not os.path.isdir(path) or os.path.islink(path):
		raise Abort(f'{path} is not a directory')
	if is_subvolume(path):
		raise Abort(f'{path} is already a subvolume')
	mount_target, fstype = findmnt(path)
	if fstype != 'btrfs':
		raise Abort(f'{path} is on {fstype}, not btrfs')
	if mount_target == path:
		raise Abort(f'{path} is a mountpoint')
	old = path + OLD_SUFFIX
	if os.path.lexists(old):
		raise Abort(f'{old} already exists; finish or clean up the previous run first')

	say(f'scanning {path} ...')
	entries, nested = scan(path)
	say('  ' + summarize(entries))
	if nested:
		raise Abort('nested subvolumes would be flattened into plain directories:\n  '
			+ '\n  '.join(nested))

	hits, unreadable = procs_using(path)
	if hits:
		listing = '\n  '.join(f'{pid} {comm}' for pid, comm in sorted(hits.items()))
		if not force:
			raise Abort(f'processes have files under {path} open (use --force to ignore):\n  '
				+ listing)
		say(f'WARNING: proceeding despite open files:\n  {listing}')
	if unreadable and os.geteuid() != 0:
		say(f'WARNING: {unreadable} processes not inspectable; run as root for a full open-file check')

	todo = plan_precreate(entries)
	say(f'{len(todo)} entries need their nodatacow flag set explicitly '
		f'(root + those differing from their parent)')
	for rel, kind, nocow in todo[:20]:
		say(f'  {"+C" if nocow else "-C"} {kind} {rel or "."}')
	if len(todo) > 20:
		say(f'  ... and {len(todo) - 20} more')

	if dry_run:
		say('dry run; would now:')
		say(f'  mv {path} {old}')
		say(f'  btrfs subvolume create {path}')
		say('  (pre-create the entries above)')
		say(f'  cp -a --reflink=always {old}/. {path}/')
		say('  verify' + (', rm -rf old copy' if delete_old else ''))
		return 0

	say(f'mv {path} {old}')
	os.rename(path, old)
	try:
		say(f'btrfs subvolume create {path}')
		subprocess.run(['btrfs', 'subvolume', 'create', path], check=True,
			stdout=subprocess.DEVNULL)
		say('replicating nodatacow flags ...')
		precreate(path, todo)
		say(f'cp -a --reflink=always {old}/. {path}/')
		subprocess.run(['cp', '-a', '--reflink=always', old + '/.', path + '/'], check=True)
	except (Abort, subprocess.CalledProcessError, OSError) as err:
		say(f'FAILED: {err}')
		say(f'the original data is intact at {old}; the partial subvolume is at {path}.')
		say(f'to roll back:  btrfs subvolume delete {path}  (or rm -rf {path});  mv {old} {path}')
		return 1

	say('verifying ...')
	problems = verify(path, entries)
	if problems:
		for problem in problems[:50]:
			say('  ' + problem)
		if len(problems) > 50:
			say(f'  ... and {len(problems) - 50} more')
		say(f'FAILED verification; old copy kept at {old}')
		return 1
	say('  ok, both trees match')

	if delete_old:
		say(f'rm -rf {old}')
		shutil.rmtree(old)
	else:
		say(f'old copy kept at {old} (shares extents with the new subvolume; '
			f'delete it once the new one is proven:  rm -rf {old})')
	return 0


def main():
	doc = __doc__ or ''
	parser = argparse.ArgumentParser(description=doc.split('\n\n')[0],
		formatter_class=argparse.RawDescriptionHelpFormatter, epilog=doc)
	parser.add_argument('path', help='directory on btrfs to turn into a subvolume')
	parser.add_argument('--dry-run', action='store_true',
		help='run the checks and print the plan, change nothing')
	parser.add_argument('--force', action='store_true',
		help='proceed even if processes have files under PATH open')
	parser.add_argument('--delete-old', action='store_true',
		help='remove the moved-aside original after a successful verification')
	args = parser.parse_args()
	try:
		return convert(args.path, args.dry_run, args.force, args.delete_old)
	except Abort as err:
		say(f'abort: {err}')
		return 2


if __name__ == '__main__':
	sys.exit(main())
