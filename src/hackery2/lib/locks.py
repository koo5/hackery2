"""flock(2)-based process locks, modeled on hillview's lock_util.py (the richer,
shared/exclusive variant lives there).

- The kernel drops a flock when the holding process dies (any signal, OOM, crash),
  so there are no stale locks and no PID-liveness machinery.
- The lock file is never unlinked: removing it while others hold/await the inode
  would split the lock. Empty lock files in /run/lock are the intended steady state.
- Shell scripts can take the same lock via flock(1):
  flock -n /run/lock/backup.py.lock -c '...'
"""
import fcntl
import os
import time

POLL_S = 5


class LockHeld(Exception):
	"""The lock is held by another process and wait=False."""


def _holders(path):
	"""best-effort live holder PIDs from /proc/locks, purely informational"""
	try:
		st = os.stat(path)
	except OSError:
		return []
	want = f"{os.major(st.st_dev):02x}:{os.minor(st.st_dev):02x}:{st.st_ino}"
	out = []
	try:
		with open('/proc/locks') as f:
			for line in f:
				# e.g.: "42: FLOCK  ADVISORY  WRITE 12345 fd:01:9184716 0 EOF"
				parts = line.split()
				if 'FLOCK' in parts:
					i = parts.index('FLOCK')
					if parts[i + 4] == want:
						out.append(parts[i + 3])
	except OSError:
		return []
	return out


def acquire(path, wait=True):
	"""
	Take an exclusive flock on `path` and hold it for the life of the process (the
	kernel releases it on exit). Returns the fd; os.close() it to release early.

	If the lock is held: with wait=True (the default), poll until it frees; with
	wait=False, raise LockHeld naming the holder - use for unattended/cron runs,
	which should fail immediately rather than queue up behind a stuck run.
	"""
	fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o666)
	try:
		# O_CREAT's mode is umask-filtered (typically to 0644), which would lock out
		# a second user (e.g. root cron vs manual run) with EACCES instead of a clean
		# wait/fail; chmod is a no-op unless we own the file
		os.chmod(path, 0o666)
	except OSError:
		pass
	while True:
		try:
			fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
			break
		except BlockingIOError:
			held = _holders(path)
			by = f" (held by pid {', '.join(held)})" if held else ""
			if not wait:
				os.close(fd)
				raise LockHeld(f"lock {path} is held{by}")
			print(f"waiting for lock {path}{by}...")
			time.sleep(POLL_S)
	print(f"acquired lock {path} (pid {os.getpid()})")
	return fd
