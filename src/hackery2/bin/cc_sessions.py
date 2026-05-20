#!/usr/bin/env python3
"""Dump Claude Code session transcripts for a project, deduped across forks.

Finds the sessions directory under ~/.claude/projects/ by slugifying the target
directory (defaults to CWD), reads every .jsonl, stitches messages together by
UUID so each message prints exactly once, and emits session-boundary headers
that mark new conversations vs. forks of earlier ones.

Grep-friendly: every content line is prefixed with `[timestamp] session-short role:`
so `grep -B 2 -A 10 pattern` stays useful. Headers start with `=== `.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


PROJECTS_DIR = Path.home() / ".claude" / "projects"


def slugify(path: str) -> str:
	"""Claude Code's project-dir slug: replace '/' and '.' with '-'."""
	return re.sub(r"[/.]", "-", path)


def resolve_sessions_dir(target: str) -> Path:
	"""Find the sessions dir for a given project path, with fallbacks."""
	target = os.path.abspath(target)
	direct = PROJECTS_DIR / slugify(target)
	if direct.is_dir():
		return direct
	# Fallback: scan projects/ for a dir whose slug matches a path that
	# resolves to the same realpath. Handles odd cases (dots in names, etc.).
	if not PROJECTS_DIR.is_dir():
		raise FileNotFoundError(f"No projects dir at {PROJECTS_DIR}")
	candidates = []
	target_real = os.path.realpath(target)
	for entry in PROJECTS_DIR.iterdir():
		if not entry.is_dir():
			continue
		# Best-effort: turn slug back into a path by replacing '-' with '/'.
		# Ambiguous, but if the resolved path matches, accept it.
		guess = "/" + entry.name.lstrip("-").replace("-", "/")
		if os.path.realpath(guess) == target_real:
			candidates.append(entry)
	if len(candidates) == 1:
		return candidates[0]
	raise FileNotFoundError(
		f"No sessions dir for {target}. Tried {direct}. "
		f"List available: ls {PROJECTS_DIR}"
	)


def short(uuid: str, n: int = 8) -> str:
	return uuid[:n] if uuid else "-" * n


def render_content(content, full: bool, show_thinking: bool) -> list[str]:
	"""Turn a message.content (str or list of blocks) into printable lines."""
	if content is None:
		return []
	if isinstance(content, str):
		return content.splitlines() or [""]
	lines = []
	for block in content:
		btype = block.get("type", "?")
		if btype == "text":
			lines.extend((block.get("text") or "").splitlines() or [""])
		elif btype == "thinking":
			if not show_thinking:
				lines.append("<thinking … (hidden; pass --thinking to show)>")
			else:
				t = block.get("thinking") or ""
				lines.append("<thinking>")
				lines.extend(t.splitlines())
				lines.append("</thinking>")
		elif btype == "tool_use":
			name = block.get("name", "?")
			inp = block.get("input", {})
			inp_s = json.dumps(inp, ensure_ascii=False)
			if not full and len(inp_s) > 400:
				inp_s = inp_s[:400] + f"… ({len(inp_s)} chars)"
			lines.append(f"<tool_use {name} id={short(block.get('id',''))}> {inp_s}")
		elif btype == "tool_result":
			tid = short(block.get("tool_use_id", ""))
			inner = block.get("content")
			if isinstance(inner, list):
				parts = []
				for ib in inner:
					if ib.get("type") == "text":
						parts.append(ib.get("text", ""))
					else:
						parts.append(json.dumps(ib, ensure_ascii=False))
				inner_s = "\n".join(parts)
			else:
				inner_s = str(inner or "")
			if not full and len(inner_s) > 800:
				inner_s = inner_s[:800] + f"… ({len(inner_s)} chars)"
			is_err = block.get("is_error")
			err = " ERROR" if is_err else ""
			lines.append(f"<tool_result for={tid}{err}>")
			lines.extend(inner_s.splitlines() or [""])
		else:
			lines.append(f"<{btype}> {json.dumps(block, ensure_ascii=False)[:200]}")
	return lines


def load_sessions(sdir: Path):
	"""Return list of (session_id, jsonl_path, [conv_records], {all_uuids_in_file}).

	conv_records are filtered to user / assistant / summary. all_uuids_in_file
	covers every line so we can tell when a parent is a non-conversational
	record (e.g. SessionStart progress hook) in the same file vs. truly
	from another session."""
	sessions = []
	for jf in sorted(sdir.glob("*.jsonl")):
		sid = jf.stem
		records = []
		all_uuids = set()
		with jf.open() as fh:
			for line in fh:
				line = line.strip()
				if not line:
					continue
				try:
					d = json.loads(line)
				except json.JSONDecodeError:
					continue
				u = d.get("uuid")
				if u:
					all_uuids.add(u)
				if d.get("type") in ("user", "assistant", "summary"):
					records.append(d)
		if records:
			sessions.append((sid, jf, records, all_uuids))
	return sessions


def first_ts(records) -> str:
	for r in records:
		ts = r.get("timestamp")
		if ts:
			return ts
	return ""


def main():
	ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
	ap.add_argument("path", nargs="?", default=os.getcwd(),
		help="Project directory (default: CWD)")
	ap.add_argument("--full", action="store_true",
		help="Don't truncate tool inputs / results")
	ap.add_argument("--thinking", action="store_true",
		help="Show assistant thinking blocks")
	ap.add_argument("--list", action="store_true",
		help="Just list sessions found and exit")
	args = ap.parse_args()

	try:
		sdir = resolve_sessions_dir(args.path)
	except FileNotFoundError as e:
		print(f"error: {e}", file=sys.stderr)
		return 2

	sessions = load_sessions(sdir)
	if not sessions:
		print(f"(no conversational records in {sdir})", file=sys.stderr)
		return 1

	# Sort sessions by earliest timestamp so oldest prints first.
	sessions.sort(key=lambda s: first_ts(s[2]))

	if args.list:
		for sid, jf, recs, _ in sessions:
			print(f"{first_ts(recs)}  {sid}  ({len(recs)} msgs)  {jf}")
		return 0

	# Track every UUID we've printed so shared/forked messages print once.
	seen_uuid: dict[str, str] = {}  # uuid -> session_id that owned the print

	for sid, jf, recs, all_uuids in sessions:
		# Find the first record whose uuid is NEW (never seen before).
		first_new_idx = None
		for i, r in enumerate(recs):
			u = r.get("uuid")
			if u and u not in seen_uuid:
				first_new_idx = i
				break

		if first_new_idx is None:
			# Entire session is already covered by earlier sessions.
			print(f"=== session {short(sid)}  (no new messages; fully contained in earlier sessions) ===")
			continue

		first_new = recs[first_new_idx]
		parent_u = first_new.get("parentUuid")
		ts = first_new.get("timestamp", "")
		if parent_u and parent_u in seen_uuid:
			# Shared a previously-printed conversational message → real fork.
			origin = seen_uuid[parent_u]
			header = (f"=== session {short(sid)}  FORK of {short(origin)} "
				f"at parent {short(parent_u)}  [{ts}]  file={jf.name} ===")
		elif parent_u is None or parent_u in all_uuids:
			# Root, or parent is a non-conversational record in this same
			# file (e.g. SessionStart progress hook). Fresh conversation.
			header = f"=== session {short(sid)}  NEW CONVERSATION  [{ts}]  file={jf.name} ==="
		else:
			# Parent referenced but not found anywhere: could be a resumed
			# session whose origin file was deleted.
			header = (f"=== session {short(sid)}  ORPHAN START "
				f"(parent {short(parent_u)} not seen)  [{ts}]  file={jf.name} ===")
		print(header)

		for r in recs[first_new_idx:]:
			u = r.get("uuid")
			if u and u in seen_uuid:
				continue
			if u:
				seen_uuid[u] = sid
			t = r.get("type")
			ts = r.get("timestamp", "")
			prefix = f"[{ts}] {short(sid)}"
			if t == "summary":
				text = r.get("summary") or r.get("message", {}).get("content") or ""
				print(f"{prefix} summary: {text}")
				continue
			msg = r.get("message", {})
			role = msg.get("role", t)
			content_lines = render_content(msg.get("content"), args.full, args.thinking)
			if not content_lines:
				print(f"{prefix} {role}:")
			else:
				print(f"{prefix} {role}: {content_lines[0]}")
				for ln in content_lines[1:]:
					print(f"{prefix}   {ln}")
	return 0


if __name__ == "__main__":
	sys.exit(main())
