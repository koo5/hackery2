#!/usr/bin/env python3
"""Dump Claude Code session transcripts for a project, deduped across forks.

Finds the sessions directory under ~/.claude/projects/ by slugifying the target
directory (defaults to CWD), reads every .jsonl, stitches messages together by
UUID so each message prints exactly once, and emits session-boundary headers
that mark new conversations vs. forks of earlier ones.

Grep-friendly: every content line is prefixed with `[timestamp] session-short role:`
so `grep -B 2 -A 10 pattern` stays useful. Headers start with `=== `.

Use --list for a flat listing or --tree for a `git log --graph --oneline --all`
view of the message DAG (deduped across all session files), with rails showing
where sessions fork from a shared parent message. By default --tree shows only
the prompts you typed — the navigate view, for telling threads apart and spotting
where you forked, without the tool-call noise; add --full for one row per message.

Use --git-export DIR to materialise that same DAG as a throwaway git repo (one
commit per prompt, or per message with --all-messages) so you can explore the
fork history in any git GUI: `gitk --all`, git gui, tig, lazygit, etc. Session
ids ride along in each commit subject and as `sess/<id>` branches at the tips.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
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


def _user_texts(rec) -> list[str]:
	"""Plain-text strings a user record carries (skips tool_result/other blocks)."""
	content = rec.get("message", {}).get("content")
	if isinstance(content, str):
		return [content]
	if isinstance(content, list):
		return [b.get("text", "") for b in content if b.get("type") == "text"]
	return []


def is_prompt(rec) -> bool:
	"""True for a turn the human actually typed.

	Excludes assistant/tool records, meta records, and XML-ish wrappers (system
	reminders, command stdout, tool_result-only user turns) — i.e. the noise that
	makes the full message graph hard to navigate."""
	if rec.get("type") != "user" or rec.get("isMeta"):
		return False
	for text in _user_texts(rec):
		t = " ".join((text or "").split())
		if t and not t.startswith("<"):
			return True
	return False


def prompt_text(rec, maxlen: int = 100) -> str:
	"""The first real typed line of a user prompt, whitespace-collapsed."""
	for text in _user_texts(rec):
		t = " ".join((text or "").split())
		if t and not t.startswith("<"):
			return t[:maxlen] + ("…" if len(t) > maxlen else "")
	return ""


def session_title(recs, start_idx: int = 0, maxlen: int = 70) -> str:
	"""Best-effort one-line label: the first real user prompt in the session."""
	for r in recs[start_idx:]:
		if is_prompt(r):
			return prompt_text(r, maxlen)
	return ""


def classify_sessions(sessions):
	"""Single dedup pass returning fork relationships and per-session ownership.

	`sessions` must already be sorted oldest-first. For each session returns a
	dict with: sid, jf, recs, all_uuids, first_new_idx (None if fully
	contained), ts (of the first new message), kind (NEW/FORK/ORPHAN/CONTAINED),
	parent (session id this one forks from, if any), parent_uuid, owned (set of
	uuids this session is responsible for printing), and total record count."""
	seen_uuid: dict[str, str] = {}  # uuid -> session id that first owned it
	infos = []
	for sid, jf, recs, all_uuids in sessions:
		first_new_idx = None
		for i, r in enumerate(recs):
			u = r.get("uuid")
			if u and u not in seen_uuid:
				first_new_idx = i
				break
		info = {
			"sid": sid, "jf": jf, "recs": recs, "all_uuids": all_uuids,
			"first_new_idx": first_new_idx, "ts": first_ts(recs),
			"kind": None, "parent": None, "parent_uuid": None,
			"owned": set(), "total": len(recs),
		}
		if first_new_idx is None:
			# Every uuid already printed elsewhere: a resume/duplicate. Nest it
			# under whichever session owns its first record, when known.
			info["kind"] = "CONTAINED"
			info["parent"] = seen_uuid.get(recs[0].get("uuid"))
			infos.append(info)
			continue

		first_new = recs[first_new_idx]
		parent_u = first_new.get("parentUuid")
		info["ts"] = first_new.get("timestamp") or info["ts"]
		if parent_u and parent_u in seen_uuid:
			info["kind"] = "FORK"
			info["parent"] = seen_uuid[parent_u]
			info["parent_uuid"] = parent_u
		elif parent_u is None or parent_u in all_uuids:
			info["kind"] = "NEW"
		else:
			info["kind"] = "ORPHAN"
			info["parent_uuid"] = parent_u

		owned = set()
		for r in recs[first_new_idx:]:
			u = r.get("uuid")
			if u and u in seen_uuid:
				continue
			if u:
				seen_uuid[u] = sid
				owned.add(u)
		info["owned"] = owned
		infos.append(info)
	return infos


def first_line(text: str) -> str:
	"""First non-blank line of a string, whitespace collapsed."""
	for ln in (text or "").splitlines():
		s = " ".join(ln.split())
		if s:
			return s
	return ""


def msg_oneline(rec, maxlen: int = 90) -> str:
	"""`--oneline`-style label for one message: role tag + content gist.

	Picks a representative block (text wins; otherwise the first tool_use /
	tool_result / thinking) so the line reflects what the message actually did."""
	msg = rec.get("message", {})
	role = msg.get("role", rec.get("type", "?"))
	tag = {"user": "U", "assistant": "A"}.get(role, (role[:1] or "?").upper())
	content = msg.get("content")
	gist = ""
	if isinstance(content, str):
		gist = first_line(content)
	elif isinstance(content, list):
		text_block = next(
			(b for b in content if b.get("type") == "text" and (b.get("text") or "").strip()),
			None,
		)
		if text_block:
			gist = first_line(text_block.get("text", ""))
		elif content:
			b = content[0]
			bt = b.get("type")
			if bt == "tool_use":
				inp = json.dumps(b.get("input", {}), ensure_ascii=False)
				gist = f"⚙ {b.get('name', '?')} {first_line(inp)}"
			elif bt == "tool_result":
				inner = b.get("content")
				if isinstance(inner, list):
					txt = " ".join(ib.get("text", "") for ib in inner if ib.get("type") == "text")
				else:
					txt = str(inner or "")
				err = "ERROR " if b.get("is_error") else ""
				gist = f"↩ {err}{first_line(txt)}"
			elif bt == "thinking":
				gist = "💭 " + first_line(b.get("thinking", ""))
			else:
				gist = f"<{bt}>"
	gist = " ".join(gist.split())
	if len(gist) > maxlen:
		gist = gist[: maxlen - 1] + "…"
	return f"{tag} {gist}" if gist else tag


def build_message_graph(sdir: Path, is_node=None):
	"""Dedup every message across all session files into one conversation DAG.

	`is_node(record)` selects which records become graph nodes (default: every
	user/assistant message). Returns (nodes, parent_of) where nodes maps uuid ->
	the record (first occurrence; forks duplicate shared history, so any copy
	will do) and parent_of maps each node uuid to its nearest ancestor *node*
	uuid (walking through any records that sit in the parentUuid chain but aren't
	themselves nodes), or None for a root. This is the `--all` view: a fork is
	just a message with two children, where two sessions branched from one
	parent."""
	if is_node is None:
		def is_node(d):
			return d.get("type") in ("user", "assistant")
	nodes = {}        # uuid -> record selected by is_node
	link = {}         # uuid -> parentUuid, for EVERY record (keeps chain intact)
	for jf in sorted(sdir.glob("*.jsonl")):
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
				if not u:
					continue
				link.setdefault(u, d.get("parentUuid"))
				if is_node(d):
					nodes.setdefault(u, d)

	def nearest_node_ancestor(u):
		p = link.get(u)
		seen = set()
		while p is not None and p not in nodes:
			if p in seen:  # defensive: never loop on a malformed chain
				return None
			seen.add(p)
			p = link.get(p)
		return p if p in nodes else None

	parent_of = {u: nearest_node_ancestor(u) for u in nodes}
	return nodes, parent_of


def graph_order(ids, parent_of, ts_of):
	"""Newest-first order that still emits every child before its parent.

	`git log --graph` only renders newest-first (`--graph --reverse` is broken
	in git for exactly this reason): the rail layout needs a parent's lane to
	stay open until every child lane has reached it. A node becomes emittable
	once all its children are emitted; among those we always take the most
	recent, which approximates git's date-order."""
	child_count = {i: 0 for i in ids}
	for i in ids:
		p = parent_of(i)
		if p is not None and p in child_count:
			child_count[p] += 1
	available = [i for i in ids if child_count[i] == 0]
	order = []
	while available:
		nid = max(available, key=ts_of)
		available.remove(nid)
		order.append(nid)
		p = parent_of(nid)
		if p is not None and p in child_count:
			child_count[p] -= 1
			if child_count[p] == 0:
				available.append(p)
	return order


def render_rails(order, parent_of, label_of) -> list[str]:
	"""Lay out nodes (already in newest-first, child-before-parent order) as a
	`git log --graph`-style rail diagram. Each node is one `*` row; a node's lane
	stays open (`|`) until its parent appears below, where lanes converge (`|/`).
	Nodes sharing no history run in parallel lanes, like independent branches."""
	lanes = []  # lanes[col] = node-id this lane is waiting to reach, or None
	lines = []
	for nid in order:
		hits = [c for c, l in enumerate(lanes) if l == nid]
		if hits:
			mycol, extra = hits[0], hits[1:]
		else:
			# A branch tip (no descendant displayed yet): take a free lane.
			mycol = next((c for c, l in enumerate(lanes) if l is None), len(lanes))
			if mycol == len(lanes):
				lanes.append(nid)
			else:
				lanes[mycol] = nid
			extra = []

		active = [c for c, l in enumerate(lanes) if l is not None]

		# Convergence row: extra child lanes slope down-left into mycol.
		if extra:
			row = [" "] * (2 * max(active) + 1)
			for c in active:
				row[2 * c] = "|"
			for c in extra:
				row[2 * c] = " "
				row[2 * c - 1] = "/"
			lines.append("".join(row).rstrip())
			for c in extra:
				lanes[c] = None
			active = [c for c, l in enumerate(lanes) if l is not None]

		# Node row: `*` at this lane, `|` for every other still-open lane.
		row = [" "] * (2 * max(active) + 1)
		for c in active:
			row[2 * c] = "|"
		row[2 * mycol] = "*"
		lines.append(f"{''.join(row).rstrip()} {label_of(nid)}")

		lanes[mycol] = parent_of(nid)  # lane now waits for the parent (None at a root)
		while lanes and lanes[-1] is None:
			lanes.pop()
	return lines


def print_graph(sdir: Path, full: bool = False):
	"""Render the project's message DAG as a `git log --graph`-style oneline log.

	Two zoom levels on the same graph, picked by `full`:

	- default (navigate zoom): one row per prompt you actually typed — the intent
	  skeleton across every thread. Assistant/tool/thinking noise is dropped, but
	  the fork structure is preserved exactly, because you only ever fork *at* a
	  prompt: two threads share an identical typed prefix and then diverge on the
	  line where you said something different, so you recognise the split by your
	  own words. Parent links hop over the dropped messages.
	- full (inspect zoom): one row per message, the complete topology."""
	nodes, parent_of = build_message_graph(sdir, None if full else is_prompt)
	if not nodes:
		return

	def ts_of(u):
		return nodes[u].get("timestamp") or ""

	def label_of(u):
		t = ts_of(u)[5:16].replace("T", " ")  # MM-DD HH:MM
		gist = msg_oneline(nodes[u]) if full else prompt_text(nodes[u])
		return f"{short(u)} [{t}] {gist}"

	order = graph_order(list(nodes), lambda u: parent_of.get(u), ts_of)
	print("\n".join(render_rails(order, lambda u: parent_of.get(u), label_of)))


def to_epoch(ts: str) -> int:
	"""Unix seconds from an ISO-8601 timestamp like 2026-06-23T18:40:43.123Z."""
	if not ts:
		return 0
	s = ts.strip().replace("Z", "+00:00")
	for candidate in (s, re.sub(r"\.\d+", "", s)):
		try:
			return int(datetime.fromisoformat(candidate).timestamp())
		except ValueError:
			continue
	return 0


def message_text(rec) -> str:
	"""Full readable text of a message (tool calls/results expanded)."""
	content = rec.get("message", {}).get("content")
	return "\n".join(render_content(content, full=True, show_thinking=True))


def export_git(sdir: Path, outdir: str, all_messages: bool = False, force: bool = False) -> int:
	"""Materialise the message DAG as a throwaway git repo so it can be browsed
	with any git history GUI (gitk, git gui, tig, lazygit, VS Code Git Graph…).

	Each node becomes a commit (parentUuid -> git parent, message timestamp ->
	commit date), the session id is sneaked into both the commit subject and a
	`sess/<id>` branch at that session's tip, and the message body is written to
	`msg/<uuid>.md` so the GUI's diff/patch pane shows the message itself. By
	default one commit per user prompt; --all-messages commits the full DAG."""
	nodes, parent_of = build_message_graph(sdir, None if all_messages else is_prompt)
	if not nodes:
		print("error: no matching messages to export", file=sys.stderr)
		return 1

	out = Path(outdir).expanduser().resolve()
	if out.exists() and any(out.iterdir()) and not force:
		print(f"error: {out} is not empty (pass --force to reuse it)", file=sys.stderr)
		return 2
	out.mkdir(parents=True, exist_ok=True)
	if not (out / ".git").exists():
		subprocess.run(["git", "init", "-q", "-b", "main", str(out)], check=True)
	else:
		# Re-export into an existing repo: drop our own refs from the prior run
		# so stale session branches don't linger (leaves any other refs alone).
		prior = subprocess.run(
			["git", "-C", str(out), "for-each-ref", "--format=%(refname)", "refs/heads/sess/"],
			capture_output=True, text=True, check=False,
		).stdout.split()
		if prior:
			subprocess.run(["git", "-C", str(out), "update-ref", "--stdin"],
				input="".join(f"delete {r}\n" for r in prior), text=True, check=False)

	def ts_of(u):
		return nodes[u].get("timestamp") or ""

	newest_first = graph_order(list(nodes), lambda u: parent_of.get(u), ts_of)
	order = list(reversed(newest_first))  # parents before children, for fast-import

	buf = bytearray()

	def w(s):
		buf.extend(s.encode())

	def wdata(b: bytes):
		buf.extend(f"data {len(b)}\n".encode())
		buf.extend(b)
		buf.extend(b"\n")

	mark = {}
	counter = 0
	for u in order:
		rec = nodes[u]
		role = rec.get("message", {}).get("role") or rec.get("type") or "?"
		sid = rec.get("sessionId") or ""
		ts = rec.get("timestamp") or ""
		body = message_text(rec)
		ident = f"{role} <{role}@claude.local>"
		md = f"# {role} · {ts}\n\nsession: {sid}\nuuid: {u}\n\n{body}\n".encode()
		subject = f"[{short(sid)}] {msg_oneline(rec, maxlen=68)}"
		msg = "\n".join([
			subject, "", body, "", "---",
			f"Session: {sid}", f"UUID: {u}", f"Time: {ts}", f"Role: {role}",
		]).encode()

		counter += 1
		bmark = counter
		w("blob\n")
		w(f"mark :{bmark}\n")
		wdata(md)

		counter += 1
		cmark = counter
		mark[u] = cmark
		p = parent_of.get(u)
		parented = p is not None and p in mark
		if not parented:
			w("reset refs/heads/import\n")  # leave branch unborn -> a root commit
		w("commit refs/heads/import\n")
		w(f"mark :{cmark}\n")
		w(f"author {ident} {to_epoch(ts)} +0000\n")
		w(f"committer {ident} {to_epoch(ts)} +0000\n")
		wdata(msg)
		if parented:
			w(f"from :{mark[p]}\n")
		w(f"M 100644 :{bmark} msg/{u}.md\n\n")

	# Ref every leaf (a message with no children) so the whole DAG — including
	# abandoned retry branches — is reachable and shows up in `gitk --all`.
	# Label each leaf by its session id; only suffix with the leaf uuid when a
	# session branched and so has more than one tip.
	child_count = {u: 0 for u in nodes}
	for u in nodes:
		p = parent_of.get(u)
		if p in child_count:
			child_count[p] += 1
	leaves_by_session = {}
	for u in order:
		if child_count[u] == 0:
			leaves_by_session.setdefault(nodes[u].get("sessionId") or "unknown", []).append(u)
	branches = 0
	for sid, leaves in leaves_by_session.items():
		for u in leaves:
			name = f"sess/{sid}" if len(leaves) == 1 else f"sess/{sid}__{u[:8]}"
			w(f"reset refs/heads/{name}\nfrom :{mark[u]}\n\n")
			branches += 1
	w(f"reset refs/heads/main\nfrom :{mark[newest_first[0]]}\n\n")

	subprocess.run(
		["git", "-C", str(out), "fast-import", "--quiet", "--date-format=raw"],
		input=bytes(buf), check=True,
	)
	subprocess.run(["git", "-C", str(out), "update-ref", "-d", "refs/heads/import"], check=False)
	subprocess.run(["git", "-C", str(out), "checkout", "-q", "-f", "main"], check=False)

	print(f"Exported {len(order)} commits across {branches} branches to {out}")
	print(f"Browse it:  (cd {out}; gitk --all)")
	print(f"      or:   git -C {out} log --graph --oneline --all")
	return 0


def main():
	ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
	ap.add_argument("path", nargs="?", default=os.getcwd(),
		help="Project directory (default: CWD)")
	ap.add_argument("--full", action="store_true",
		help="Show full detail: untruncated tool inputs/results in the dump; "
			"every message (not just prompts) in --tree")
	ap.add_argument("--thinking", action="store_true",
		help="Show assistant thinking blocks")
	ap.add_argument("--list", action="store_true",
		help="Just list sessions found and exit")
	ap.add_argument("--tree", action="store_true",
		help="Show the message DAG as a git-log-graph oneline log (just your "
			"prompts; add --full for every message) and exit")
	ap.add_argument("--git-export", metavar="DIR",
		help="Export the message DAG as a throwaway git repo at DIR (browse with gitk --all)")
	ap.add_argument("--all-messages", action="store_true",
		help="With --git-export: one commit per message (default: one per user prompt)")
	ap.add_argument("--force", action="store_true",
		help="With --git-export: allow a non-empty target directory")
	args = ap.parse_args()

	try:
		sdir = resolve_sessions_dir(args.path)
	except FileNotFoundError as e:
		print(f"error: {e}", file=sys.stderr)
		return 2

	if args.git_export:
		return export_git(sdir, args.git_export, args.all_messages, args.force)

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

	if args.tree:
		# `git log --graph --oneline --all` over the message DAG, deduped across
		# all session files, rails showing forks. Default: one row per typed
		# prompt (navigate zoom); --full: one row per message (inspect zoom).
		print_graph(sdir, args.full)
		return 0

	# One pass establishes fork relationships and which uuids each session is
	# responsible for printing (so shared/forked messages print exactly once).
	infos = classify_sessions(sessions)

	for info in infos:
		sid, jf, recs = info["sid"], info["jf"], info["recs"]
		first_new_idx = info["first_new_idx"]

		if first_new_idx is None:
			# Entire session is already covered by earlier sessions.
			print(f"=== session {short(sid)}  (no new messages; fully contained in earlier sessions) ===")
			continue

		ts = info["ts"]
		kind = info["kind"]
		if kind == "FORK":
			# Shared a previously-printed conversational message → real fork.
			header = (f"=== session {short(sid)}  FORK of {short(info['parent'])} "
				f"at parent {short(info['parent_uuid'])}  [{ts}]  file={jf.name} ===")
		elif kind == "NEW":
			# Root, or parent is a non-conversational record in this same
			# file (e.g. SessionStart progress hook). Fresh conversation.
			header = f"=== session {short(sid)}  NEW CONVERSATION  [{ts}]  file={jf.name} ==="
		else:
			# Parent referenced but not found anywhere: could be a resumed
			# session whose origin file was deleted.
			header = (f"=== session {short(sid)}  ORPHAN START "
				f"(parent {short(info['parent_uuid'])} not seen)  [{ts}]  file={jf.name} ===")
		print(header)

		for r in recs[first_new_idx:]:
			u = r.get("uuid")
			if u and u not in info["owned"]:
				continue
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
