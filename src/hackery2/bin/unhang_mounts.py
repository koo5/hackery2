#!/usr/bin/env python3
"""Detect and recover hung FUSE / network filesystem mounts.

A single unresponsive mount (dead sshfs, stale NFS, unreachable CIFS share)
makes ``df`` -- and any process that traverses ``/`` -- block forever, because
``statfs()``/``stat()`` on that mount enters uninterruptible sleep waiting for a
server that will never answer.

This tool probes every network/FUSE mount with a hard timeout. For each one
that hangs (or already reports "Transport endpoint is not connected") it:

  1. aborts the FUSE connection via ``/sys/fs/fuse/connections/<minor>/abort``
     so any pending I/O fails fast with EIO instead of blocking, then
  2. lazily unmounts the mountpoint, and
  3. reaps the leftover mount-helper process (sshfs, mount.fuse, ...).

By default it only *reports* what is hung. Pass ``--fix`` to actually recover.

This is the manual recipe that fixed a dead ``ktiff.internal`` sshfs:

    echo 1 > /sys/fs/fuse/connections/<minor>/abort
    fusermount -u <mountpoint>
    kill -9 <sshfs-pid>
"""

import argparse
import os
import re
import signal
import subprocess
import sys

# Filesystem types worth probing: they can stall on an unreachable backend.
# Local fs (ext4, btrfs, squashfs, tmpfs, ...) never hang on statfs, so skip
# them -- probing 150 squashfs loop mounts is just noise.
NETWORK_FS_PREFIXES = ("fuse", "nfs", "cifs", "smb", "ceph", "glusterfs", "9p")

PROBE_TIMEOUT = 5  # seconds to wait for statfs before declaring a mount hung


class Mount:
	"""One mount entry from /proc/self/mountinfo that we might probe."""

	def __init__(self, mountpoint, fstype, major, minor, source):
		self.mountpoint = mountpoint
		self.fstype = fstype
		self.major = major
		self.minor = minor
		self.source = source
		self.status = None  # "ok" | "hung" | "dead" | "error"

	@property
	def is_fuse(self):
		return self.fstype.startswith("fuse")

	@property
	def fuse_conn_path(self):
		"""Path to the FUSE control dir for this mount (major is 0 for FUSE)."""
		return "/sys/fs/fuse/connections/{}".format(self.minor)


def parse_mounts():
	"""Read /proc/self/mountinfo and return the network/FUSE mounts.

	Uses /proc directly rather than calling ``mount``/``findmnt`` so that we
	never block on the very mounts we are trying to diagnose.
	"""
	mounts = []
	with open("/proc/self/mountinfo", "r") as fh:
		for line in fh:
			fields = line.split()
			try:
				sep = fields.index("-")
			except ValueError:
				continue
			mountpoint = fields[4]
			major, _, minor = fields[2].partition(":")
			fstype = fields[sep + 1]
			source = fields[sep + 2] if len(fields) > sep + 2 else "?"
			if fstype.startswith(NETWORK_FS_PREFIXES):
				mounts.append(Mount(mountpoint, fstype, major, int(minor), source))
	return mounts


def probe(mount, timeout):
	"""Classify a mount by attempting statfs under a hard timeout.

	Runs the probe in a child process (``timeout -k ... stat -f``) so that an
	uninterruptible-sleep hang can never freeze this tool: ``timeout`` escalates
	to SIGKILL, and we wrap that in our own slightly longer wall-clock guard.
	"""
	try:
		result = subprocess.run(
			["timeout", "-k", "2", str(timeout), "stat", "-f", mount.mountpoint],
			stdout=subprocess.DEVNULL,
			stderr=subprocess.PIPE,
			timeout=timeout + 5,
		)
	except subprocess.TimeoutExpired:
		mount.status = "hung"
		return
	stderr = result.stderr.decode("utf-8", "replace").lower()
	if result.returncode == 124 or result.returncode == 137:
		mount.status = "hung"  # killed by `timeout` -> statfs never returned
	elif "transport endpoint is not connected" in stderr:
		mount.status = "dead"  # connection already torn down, mount lingering
	elif result.returncode == 0:
		mount.status = "ok"
	else:
		mount.status = "error"  # e.g. permission denied -- not a hang


def find_helper_pids(mountpoint):
	"""Return PIDs of mount-helper processes (sshfs, mount.fuse, ...) for a path.

	After ``fusermount -u`` detaches a dead sshfs, its userspace process is
	often orphaned and must be killed explicitly.
	"""
	pids = []
	for entry in os.listdir("/proc"):
		if not entry.isdigit():
			continue
		try:
			with open("/proc/{}/cmdline".format(entry), "rb") as fh:
				cmdline = fh.read().replace(b"\x00", b" ").decode("utf-8", "replace")
		except OSError:
			continue
		if not cmdline:
			continue
		# Match a mount helper that references this exact mountpoint.
		if re.search(r"\b(sshfs|mount\.\w+|fuse)\b", cmdline) and mountpoint in cmdline:
			pids.append(int(entry))
	return pids


def abort_fuse(mount, verbose=True):
	"""Force-fail in-flight FUSE I/O so stuck processes unblock immediately."""
	if not mount.is_fuse:
		return False
	abort = os.path.join(mount.fuse_conn_path, "abort")
	if not os.path.exists(abort):
		return False
	try:
		with open(abort, "w") as fh:
			fh.write("1")
		if verbose:
			print("    aborted FUSE connection {}".format(mount.minor))
		return True
	except OSError as exc:
		print("    could not abort FUSE connection {}: {}".format(mount.minor, exc))
		return False


def unmount(mount, verbose=True):
	"""Detach a mount, preferring the userspace fuse unmount, then lazy umount."""
	attempts = []
	if mount.is_fuse:
		attempts.append(["fusermount", "-u", mount.mountpoint])
	attempts.append(["umount", "-l", mount.mountpoint])  # lazy: detach now, clean up async
	for cmd in attempts:
		try:
			result = subprocess.run(
				cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=15
			)
		except (subprocess.TimeoutExpired, FileNotFoundError):
			continue
		if result.returncode == 0:
			if verbose:
				print("    unmounted via: {}".format(" ".join(cmd)))
			return True
	# Still mounted? Surface why the last attempt failed.
	if verbose and result.stdout:
		print("    unmount failed: {}".format(result.stdout.decode("utf-8", "replace").strip()))
	return False


def reap_helpers(mount, verbose=True):
	"""SIGTERM then SIGKILL any leftover helper process for the mount."""
	pids = find_helper_pids(mount.mountpoint)
	for sig in (signal.SIGTERM, signal.SIGKILL):
		alive = []
		for pid in pids:
			try:
				os.kill(pid, sig)
				alive.append(pid)
			except ProcessLookupError:
				pass
			except PermissionError:
				print("    cannot signal pid {} (need root?)".format(pid))
		pids = alive
		if not pids:
			break
	survivors = [p for p in pids if os.path.exists("/proc/{}".format(p))]
	if verbose and not survivors:
		print("    helper process(es) reaped")
	return not survivors


def recover(mount):
	"""Run the full abort -> unmount -> reap recovery for one stuck mount."""
	print("  recovering {} ({})".format(mount.mountpoint, mount.status))
	abort_fuse(mount)
	unmount(mount)
	reap_helpers(mount)


def main():
	parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument("--fix", action="store_true", help="actually recover hung mounts (default: report only)")
	parser.add_argument("--timeout", type=int, default=PROBE_TIMEOUT, help="seconds to wait per statfs probe (default: %(default)s)")
	parser.add_argument("--all", action="store_true", help="show OK mounts too, not just problems")
	args = parser.parse_args()

	mounts = parse_mounts()
	if not mounts:
		print("No FUSE/network mounts found.")
		return 0

	print("Probing {} network/FUSE mount(s)...".format(len(mounts)))
	stuck = []
	for mount in mounts:
		probe(mount, args.timeout)
		if mount.status in ("hung", "dead"):
			stuck.append(mount)
			print("  [{}] {}  <- {}".format(mount.status.upper(), mount.mountpoint, mount.source))
		elif args.all:
			print("  [{}] {}".format(mount.status.upper(), mount.mountpoint))

	if not stuck:
		print("All mounts responsive. `df` should not hang.")
		return 0

	if not args.fix:
		print("\n{} stuck mount(s). Re-run with --fix to abort + unmount them.".format(len(stuck)))
		return 1

	print("\nRecovering {} stuck mount(s):".format(len(stuck)))
	for mount in stuck:
		recover(mount)
	print("\nDone. Try `df` again.")
	return 0


if __name__ == "__main__":
	sys.exit(main())
