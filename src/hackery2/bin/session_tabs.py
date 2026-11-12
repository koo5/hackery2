#!/usr/bin/env python3
"""Open saved Codex/Claude sessions in Konsole tabs, attached through tmux."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys


DEFAULT_HOST = "dev4-3"
DEFAULT_CWD = "~/repos/koo5/hillview/0/"


def nonempty(value, label):
	if not isinstance(value, str) or not value.strip():
		raise ValueError(f"{label} must be a nonempty string")
	if any(ord(char) < 32 or ord(char) == 127 for char in value):
		raise ValueError(f"{label} must not contain control characters")
	return value


def tmux_name(session):
	# tmux forbids periods and colons. Keep ordinary names/UUIDs compatible
	# with sessions made by dev43clautmux.sh; hash changed names to avoid clashes.
	if re.fullmatch(r"[A-Za-z0-9_-]{1,100}", session):
		return session
	stem = re.sub(r"[^A-Za-z0-9_-]", "_", session)[:80]
	return stem + "-" + hashlib.sha256(session.encode()).hexdigest()[:12]


def normalize(entry, host, cwd):
	if isinstance(entry, str):
		tool, separator, session = entry.partition(":")
		if not separator:
			raise ValueError(f"expected codex:NAME or claude:NAME, got {entry!r}")
		entry = {"tool": tool, "session": session}
	if not isinstance(entry, dict):
		raise ValueError("each entry must be a tool:NAME string or an object")
	unknown = set(entry) - {"tool", "session", "host", "cwd", "tmux"}
	if unknown:
		raise ValueError(f"unknown entry fields: {', '.join(sorted(unknown))}")
	tool = entry.get("tool")
	if tool not in ("codex", "claude"):
		raise ValueError("tool must be 'codex' or 'claude'")
	session = nonempty(entry.get("session"), "session")
	if session.startswith("-"):
		raise ValueError("session must not begin with '-'")
	host = nonempty(entry.get("host", host), "host")
	if host.startswith("-") or any(char.isspace() for char in host):
		raise ValueError("host must be an SSH destination, or 'local'")
	cwd = nonempty(entry.get("cwd", cwd), "cwd")
	name = nonempty(entry.get("tmux", tmux_name(session)), "tmux")
	if "." in name or ":" in name:
		raise ValueError("tmux name must not contain '.' or ':'")
	return {"tool": tool, "session": session, "host": host, "cwd": cwd, "tmux": name}


def shell_path(path):
	# Expand only the target machine's home, never shell syntax from the file.
	if path == "~":
		return '"$HOME"'
	if path.startswith("~/"):
		return '"$HOME"/' + shlex.quote(path[2:])
	if not path.startswith("/"):
		return '"$HOME"/' + shlex.quote(path)
	return shlex.quote(path)


def attach_command(entry):
	if entry["tool"] == "codex":
		resume = ["codex", "resume", entry["session"]]
	else:
		resume = ["claude", "--resume", entry["session"]]
	# -A checks for an existing session and attaches atomically. A single
	# shell-command argument also works on older tmux versions.
	return (
		"exec tmux new-session -A -s " + shlex.quote(entry["tmux"])
		+ " -c " + shell_path(entry["cwd"])
		+ " " + shlex.quote("exec " + shlex.join(resume))
	)


def session_command(entry):
	command = attach_command(entry)
	if entry["host"] == "local":
		attach = ["sh", "-c", command]
	else:
		# SSH passes a command string through the remote user's shell (often
		# fish here). Explicit sh keeps HOME expansion and quoting predictable.
		attach = ["ssh", "-t", "--", entry["host"], shlex.join(["sh", "-c", command])]
	return attach


def dbus_call(*arguments):
	client = next((path for name in ("qdbus6", "qdbus", "qdbus-qt5")
	               if (path := shutil.which(name))), None)
	if not client:
		raise RuntimeError("install qdbus (Qt D-Bus command-line tools) to create Konsole tabs")
	result = subprocess.run([client, *arguments], text=True, capture_output=True, timeout=10)
	if result.returncode:
		raise RuntimeError("Konsole D-Bus call failed: " + (result.stderr or result.stdout).strip())
	return result.stdout.strip()


def select_window(service=None, window=None):
	service = service or os.environ.get("KONSOLE_DBUS_SERVICE")
	if not service:
		services = [line.strip() for line in dbus_call().splitlines()
		            if line.strip().startswith("org.kde.konsole")]
		if len(services) != 1:
			raise RuntimeError("run from Konsole or specify --konsole-service (available: "
			                   + ", ".join(services) + ")")
		service = services[0]
	windows = [path for path in dbus_call(service).splitlines()
	           if re.fullmatch(r"/Windows/\d+", path)]
	window = window or os.environ.get("KONSOLE_DBUS_WINDOW")
	if window:
		if window.isdigit():
			window = "/Windows/" + window
		if window not in windows:
			raise RuntimeError(f"Konsole window {window!r} does not exist in {service}")
		return service, window
	# One Konsole process may own many windows. Find the caller's window by
	# session membership, rather than choosing whichever window is active.
	session = os.environ.get("KONSOLE_DBUS_SESSION", "").rsplit("/", 1)[-1]
	if session:
		matches = [path for path in windows if session in dbus_call(
			service, path, "org.kde.konsole.Window.sessionList").splitlines()]
		if len(matches) == 1:
			return service, matches[0]
	if len(windows) == 1:
		return service, windows[0]
	raise RuntimeError("specify --konsole-window (available: " + ", ".join(windows) + ")")


def open_tab(entry, service, window):
	# Creating the session on this exact window never launches another
	# Konsole process/window, even when single-instance reuse is disabled.
	session = dbus_call(service, window, "org.kde.konsole.Window.newSession")
	if not session.isdigit() or int(session) <= 0:
		raise RuntimeError(f"Konsole returned an invalid session ID: {session!r}")
	path = "/Sessions/" + session
	title = f"{entry['session']}@{entry['host']}".replace("%", "%%")
	for context in ("0", "1"):
		dbus_call(service, path, "org.kde.konsole.Session.setTabTitleFormat", context, title)
	# The new tab's shell reads this queued command after its startup. Keep
	# that shell alive so SSH errors and tmux detach leave a usable prompt.
	dbus_call(service, path, "org.kde.konsole.Session.runCommand", shlex.join(session_command(entry)))
	return session


def main(argv=None):
	parser = argparse.ArgumentParser(
		description=__doc__,
		epilog="Example: session_tabs.py 'codex:map tiles' claude:fix-tests\n"
		       "Use --file for a JSON list with per-entry host/cwd/tmux overrides.\n"
		       "Relative directories are relative to the target host's home.",
		formatter_class=argparse.RawDescriptionHelpFormatter,
	)
	parser.add_argument("sessions", nargs="*", metavar="TOOL:NAME")
	parser.add_argument("-f", "--file", type=Path, help="JSON list of sessions")
	parser.add_argument("--host", default=DEFAULT_HOST, help="default SSH destination (or local)")
	parser.add_argument("--cwd", default=DEFAULT_CWD, help="default directory on the target host")
	parser.add_argument("--konsole-service", help="target Konsole D-Bus service (normally inherited)")
	parser.add_argument("--konsole-window", help="target window ID or /Windows/ID (normally detected)")
	parser.add_argument("--dry-run", action="store_true", help="print attachment commands without opening tabs")
	args = parser.parse_args(argv)
	try:
		entries = []
		if args.file:
			entries = json.loads(args.file.read_text())
			if not isinstance(entries, list):
				raise ValueError("session file must contain a JSON list")
		entries = [normalize(entry, args.host, args.cwd) for entry in entries + args.sessions]
		if not entries:
			raise ValueError("provide at least one TOOL:NAME or --file")
		# Validate the entire list before opening any tabs. Repeated entries
		# should not create extra tabs attached to the same tmux session.
		unique = {}
		for entry in entries:
			key = (entry["host"], entry["tmux"])
			if key in unique and entry != unique[key]:
				raise ValueError(f"conflicting entries for tmux session {key!r}")
			unique[key] = entry
	except (OSError, ValueError) as error:
		parser.error(str(error))
	if args.dry_run:
		for entry in unique.values():
			print(shlex.join(session_command(entry)))
		return 0
	try:
		service, window = select_window(args.konsole_service, args.konsole_window)
		for entry in unique.values():
			open_tab(entry, service, window)
	except (OSError, RuntimeError, subprocess.SubprocessError) as error:
		print(f"Could not open session tabs: {error}", file=sys.stderr)
		return 1
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
