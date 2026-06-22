#!/usr/bin/env python3
"""
Snapshot guest VM config dirs (default: /etc) into ~/sec/<vm>/snapshots/<ts>/,
with a sha256 manifest and an auto-diff against the most recent prior snapshot.

Trust model: the snapshot store lives on the *host*, so diffs are anchored in
data we control — not the guest's own manifests, which a compromised guest
could rewrite. Run after stopping the VM and read-only mounting its image.

Manifest format (tab-separated, value column is self-tagged so file-content
hashes can never be confused with symlink target paths):
	F	<relpath>	sha256=<hex>
	L	<relpath>	target=<raw symlink target as stored on disk>
	D	<relpath>	-
	E	<relpath>	error=<exception class>

Usage:
	snapshot.py <vm-name> <mounted-root> [--dirs etc var/spool/cron ...]
"""

import argparse
import datetime
import hashlib
import os
import subprocess
import sys
from pathlib import Path

DEFAULT_DIRS = ["etc"]


def sha256_file(path):
	h = hashlib.sha256()
	with open(path, "rb") as f:
		for chunk in iter(lambda: f.read(65536), b""):
			h.update(chunk)
	return h.hexdigest()


def build_manifest(root):
	lines = []
	for p in sorted(root.rglob("*")):
		rel = p.relative_to(root)
		# is_symlink() must come first: a symlink to a file also passes is_file(),
		# so the natural ordering would silently hash the target and lose the link.
		if p.is_symlink():
			target = os.readlink(p)
			lines.append(f"L\t{rel}\ttarget={target}")
		elif p.is_dir():
			lines.append(f"D\t{rel}\t-")
		elif p.is_file():
			try:
				lines.append(f"F\t{rel}\tsha256={sha256_file(p)}")
			except (PermissionError, OSError) as e:
				lines.append(f"E\t{rel}\terror={e.__class__.__name__}")
	return "\n".join(lines) + "\n"


def parse_manifest(text):
	out = {}
	for line in text.splitlines():
		if not line:
			continue
		parts = line.split("\t", 2)
		if len(parts) >= 2:
			out[parts[1]] = line
	return out


def diff_manifests(prev_text, cur_text):
	prev = parse_manifest(prev_text)
	cur = parse_manifest(cur_text)
	added = sorted(cur.keys() - prev.keys())
	removed = sorted(prev.keys() - cur.keys())
	changed = sorted(k for k in cur.keys() & prev.keys() if cur[k] != prev[k])
	return added, removed, changed


def find_previous_snapshot(snap_root, current):
	candidates = sorted(p for p in snap_root.iterdir() if p.is_dir() and p != current)
	return candidates[-1] if candidates else None


def print_diff(prev, added, removed, changed, limit=80):
	print(f"\ndiff vs {prev.name}:")
	print(f"  added:   {len(added)}")
	print(f"  removed: {len(removed)}")
	print(f"  changed: {len(changed)}")
	for label, items in (("+", added), ("-", removed), ("~", changed)):
		shown = items[:limit]
		for it in shown:
			print(f"  {label} {it}")
		if len(items) > limit:
			print(f"  ... and {len(items) - limit} more {label}")


def main():
	ap = argparse.ArgumentParser(
		description=__doc__,
		formatter_class=argparse.RawDescriptionHelpFormatter,
	)
	ap.add_argument("vm_name", help="logical name for this VM (becomes a dir under ~/sec/)")
	ap.add_argument("mounted_root", type=Path, help="path where the guest image is mounted (e.g. /mnt/vm)")
	ap.add_argument(
		"--dirs",
		nargs="+",
		default=DEFAULT_DIRS,
		help=f"dirs under mounted_root to snapshot (default: {DEFAULT_DIRS})",
	)
	args = ap.parse_args()

	if not args.mounted_root.is_dir():
		sys.exit(f"mounted root {args.mounted_root} is not a directory")

	sec_root = Path.home() / "sec" / args.vm_name / "snapshots"
	sec_root.mkdir(parents=True, exist_ok=True)

	ts = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
	snap = sec_root / ts
	snap.mkdir()
	print(f"snapshot: {snap}")

	any_copied = False
	for d in args.dirs:
		src = args.mounted_root / d
		if not src.is_dir():
			print(f"  skip: {src} not found", file=sys.stderr)
			continue
		dst = snap / d
		dst.parent.mkdir(parents=True, exist_ok=True)
		print(f"  copy: {src} -> {dst}")
		try:
			# -a preserves symlinks/perms/ownership/timestamps; ownership needs root
			subprocess.run(["cp", "-a", str(src), str(dst)], check=True)
		except subprocess.CalledProcessError:
			sys.exit(f"cp failed for {src} — try running as root (sudo)")
		any_copied = True

	if not any_copied:
		snap.rmdir()
		sys.exit("nothing copied; aborting (snapshot dir removed)")

	print("  manifest: hashing...")
	manifest = build_manifest(snap)
	(snap / "MANIFEST.sha256").write_text(manifest)

	prev = find_previous_snapshot(sec_root, snap)
	if prev is None:
		print(f"\nfirst snapshot for {args.vm_name}")
		return
	prev_manifest_path = prev / "MANIFEST.sha256"
	if not prev_manifest_path.exists():
		print(f"\nprevious snapshot {prev.name} has no manifest; skipping diff")
		return
	added, removed, changed = diff_manifests(prev_manifest_path.read_text(), manifest)
	print_diff(prev, added, removed, changed)


if __name__ == "__main__":
	main()
