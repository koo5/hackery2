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

Use --git-export [DIR] to materialise that same DAG as a throwaway git repo (one
commit per prompt, or per message with --full) so you can explore the fork
history in any git GUI: `gitk --all`, git gui, tig, lazygit, etc. Omit DIR to use
an auto-refreshed cache at ~/.cache/cc_sessions/<project>. Session ids ride along
in each commit subject and as `sess/<id>` branches at the tips.

Use --html [FILE] for a self-contained interactive HTML/SVG of the same graph:
gitk-style lanes coloured per session, each thread tip badged with its title,
hover for the full prompt, click a message to read it formatted in full, click
its session hash to copy the `claude --resume` command.
Use --serve [PORT] to serve that graph live on localhost, regenerated on each
request so a browser refresh reflects newly-written messages. The page lets you
switch between prompts, prompts + answers, and everything, select a session,
and toggle thinking in the Everything view. --full, --view and --thinking set
the initial display. Use --id ID (or a unique prefix) to select a session in
any output mode, including its shared history from the selected file.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, urlsplit


PROJECTS_DIR = Path.home() / ".claude" / "projects"
SESSION_UUID_INDEX_CACHE = {}


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


def session_files(sdir: Path, session_id=None):
	"""Select a session file by exact ID or unambiguous prefix."""
	files = sorted(sdir.glob("*.jsonl"))
	if not session_id:
		return files
	exact = [jf for jf in files if jf.stem == session_id]
	matches = exact or [jf for jf in files if jf.stem.startswith(session_id)]
	if len(matches) != 1:
		reason = "no matching session" if not matches else "ambiguous session prefix"
		raise ValueError(f"{reason}: {session_id}")
	return matches


def visible_record(rec, view="all", thinking=False):
	"""Filter content as well as nodes, so mixed text/tool messages stay readable."""
	if rec.get("type") not in ("user", "assistant"):
		return None
	if view == "prompts" and not is_prompt(rec):
		return None
	if view == "conversation" and not (
		is_prompt(rec) or (rec.get("type") == "assistant" and not rec.get("isMeta"))
	):
		return None
	content = rec.get("message", {}).get("content")
	if isinstance(content, list):
		content = [block for block in content
			if (thinking or block.get("type") != "thinking")
			and (view == "all" or block.get("type") == "text")]
		if not content:
			return None
	elif view != "all" and not content:
		return None
	return {**rec, "message": {**rec.get("message", {}), "content": content}}


def short(uuid: str, n: int = 8) -> str:
	return uuid[:n] if uuid else "-" * n


def esc(s) -> str:
	"""Escape text for embedding in HTML/SVG (element text and attributes)."""
	return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
		.replace('"', "&quot;"))


def tool_result_text(inner) -> str:
	"""Flatten a tool_result's content (str or list of blocks) to plain text."""
	if not isinstance(inner, list):
		return str(inner or "")
	parts = []
	for ib in inner:
		if ib.get("type") == "text":
			parts.append(ib.get("text", ""))
		elif ib.get("type") == "image":
			parts.append("[image]")
		else:
			parts.append(json.dumps(ib, ensure_ascii=False))
	return "\n".join(parts)


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
			inner_s = tool_result_text(block.get("content"))
			if not full and len(inner_s) > 800:
				inner_s = inner_s[:800] + f"… ({len(inner_s)} chars)"
			is_err = block.get("is_error")
			err = " ERROR" if is_err else ""
			lines.append(f"<tool_result for={tid}{err}>")
			lines.extend(inner_s.splitlines() or [""])
		else:
			lines.append(f"<{btype}> {json.dumps(block, ensure_ascii=False)[:200]}")
	return lines


def load_sessions(sdir: Path, session_id=None, recovery_warnings=None,
		recovered_ancestors=None):
	"""Return list of (session_id, jsonl_path, [conv_records], {all_uuids_in_file}).

	conv_records are filtered to user / assistant / summary. all_uuids_in_file
	covers every line so we can tell when a parent is a non-conversational
	record (e.g. SessionStart progress hook) in the same file vs. truly
	from another session."""
	selected_files = session_files(sdir, session_id)
	sessions = []
	compact_boundaries = []
	boundaries_by_file = {}
	for jf in selected_files:
		sid = jf.stem
		records = []
		all_uuids = set()
		file_boundaries = []
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
				if d.get("type") == "system" and d.get("subtype") == "compact_boundary":
					file_boundaries.append(d)
				if d.get("type") in ("user", "assistant", "summary"):
					records.append(d)
		if records:
			sessions.append((sid, jf, records, all_uuids))
		if file_boundaries:
			compact_boundaries.extend(file_boundaries)
			boundaries_by_file[jf] = file_boundaries
	if compact_boundaries:
		# Compaction can leave only a compact_boundary record plus a summary in
		# the resumed file. Search by UUID so unrelated, very large session logs
		# do not all need to be parsed.
		def index_source(source):
			stat = source.stat()
			cache_key = (stat.st_mtime_ns, stat.st_size)
			cached = SESSION_UUID_INDEX_CACHE.get(source)
			if cached and cached[0] == cache_key:
				return cached[1]
			by_uuid = {}
			with source.open() as fh:
				for line in fh:
					try:
						rec = json.loads(line)
					except json.JSONDecodeError:
						continue
					uuid = rec.get("uuid")
					if not uuid:
						continue
					if rec.get("type") not in ("user", "assistant", "summary"):
						rec = {key: rec.get(key) for key in (
							"uuid", "parentUuid", "type", "subtype",
							"logicalParentUuid", "timestamp", "compactMetadata")}
					by_uuid.setdefault(uuid, rec)
			SESSION_UUID_INDEX_CACHE[source] = (cache_key, by_uuid)
			return by_uuid

		def find_ancestor(uuid, preferred_source, current_source, current_records):
			# Duplicate message UUIDs can have different parentUuid links in a
			# compacted continuation and its older source log. Follow one source
			# file consistently instead of switching to the selected copy midway.
			if preferred_source and preferred_source != current_source:
				rec = index_source(preferred_source).get(uuid)
				if rec:
					return rec, preferred_source
			if preferred_source == current_source and uuid in current_records:
				return current_records[uuid], current_source
			if preferred_source and preferred_source != current_source:
				if uuid in current_records:
					return current_records[uuid], current_source
			needle = f'"uuid":"{uuid}"'
			matches = subprocess.run(
				["rg", "-l", "-0", "-F", "--glob", "*.jsonl", needle, str(sdir)],
				capture_output=True, check=False,
			)
			candidates = [Path(raw.decode()) for raw in matches.stdout.split(b"\0") if raw]
			candidates.sort(key=lambda path: (path == current_source, -path.stat().st_size))
			for source in candidates:
				rec = index_source(source).get(uuid)
				if rec:
					return rec, source
			return None, None
		for _sid, jf, records, all_uuids in sessions:
			file_boundaries = boundaries_by_file.get(jf)
			if not file_boundaries:
				continue
			present = {r.get("uuid") for r in records if r.get("uuid")}
			record_by_uuid = {r.get("uuid"): r for r in records if r.get("uuid")}
			ancestors = {}
			for boundary in file_boundaries:
				parent = boundary.get("logicalParentUuid")
				seen = set()
				missing_parent = None
				preferred_source = None
				while parent and parent not in seen:
					seen.add(parent)
					rec, preferred_source = find_ancestor(
						parent, preferred_source, jf, record_by_uuid)
					if rec is None:
						missing_parent = parent
						break
					ancestors[parent] = rec
					if rec.get("type") == "system" \
							and rec.get("subtype") == "compact_boundary":
						parent = rec.get("logicalParentUuid")
					else:
						parent = rec.get("parentUuid")
				if missing_parent:
					if recovery_warnings is not None:
						metadata = boundary.get("compactMetadata") or {}
						preserved = metadata.get("preservedSegment") or {}
						preserved_ids = ", ".join(
							f"{key}={preserved[key]}"
							for key in ("headUuid", "anchorUuid", "tailUuid")
							if preserved.get(key)
						) or "not recorded"
						recovery_warnings.append(
							f"session {short(jf.stem)}: compacted history could not be fully recovered.\n"
							f"  The compaction boundary at {boundary.get('timestamp', 'unknown time')} "
							f"is recorded in this same session file; this does not mean the earlier "
							f"conversation had a different session ID or that the file was overwritten.\n"
							f"  Ancestor lookup stopped at {missing_parent}: no record with that UUID "
							f"was found in the current project session logs. The UUID may still exist "
							f"in a backup.\n"
							f"  Backup search clues: logicalParentUuid={boundary.get('logicalParentUuid')}; "
							f"boundaryUuid={boundary.get('uuid')}; preserved {preserved_ids}.\n"
							f"  Search older copies/snapshots of ~/.claude/projects for any of those "
							f"full UUIDs, especially the logical parent. If found, restore or copy the "
							f"matching JSONL into this project’s session directory and rerun cc_sessions."
						)
			# Parent links run newest to oldest; prepend in transcript order.
			if ancestors:
				if recovered_ancestors is not None:
					recovered_ancestors.extend(ancestors.values())
				recovered = sorted(
					(r for r in ancestors.values()
						if r.get("type") in ("user", "assistant", "summary")
						and r.get("uuid") not in present),
					key=lambda r: r.get("timestamp", ""),
				)
				records[:0] = recovered
				all_uuids.update(ancestors)
			if recovery_warnings is not None and not missing_parent:
				added = sum(
					1 for rec in ancestors.values()
					if rec.get("type") in ("user", "assistant", "summary")
					and rec.get("uuid") not in present
				)
				recovery_warnings.append(
					f"INFO: session {short(jf.stem)}: compaction boundary at "
					f"{boundary.get('timestamp', 'unknown time')} points to logical parent "
					f"{boundary.get('logicalParentUuid')}. The local parent chain is intact; "
					f"recovered {added} earlier conversation records absent from this session file."
					+ (" The compacted messages may only remain in backups; search older "
						"~/.claude/projects snapshots for the logical parent and preserved UUIDs."
						if added == 0 else "")
				)
	return sessions


def first_ts(records) -> str:
	for r in records:
		ts = r.get("timestamp")
		if ts:
			return ts
	return ""


def load_titles(sdir: Path, session_id=None):
	"""Map session id -> (custom_title, ai_title) from the title records Claude
	Code writes: `/rename` appends a `custom-title` record and the auto-namer an
	`ai-title` record, both `{..., sessionId}`. Last write per session wins."""
	custom, ai = {}, {}
	for jf in session_files(sdir, session_id):
		with jf.open() as fh:
			for line in fh:
				line = line.strip()
				if not line:
					continue
				try:
					d = json.loads(line)
				except json.JSONDecodeError:
					continue
				sid = d.get("sessionId")
				if not sid:
					continue
				if d.get("type") == "custom-title" and d.get("customTitle"):
					custom[sid] = d["customTitle"]
				elif d.get("type") == "ai-title" and d.get("aiTitle"):
					ai[sid] = d["aiTitle"]
	return custom, ai


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


def build_message_graph(sdir: Path, is_node=None, session_id=None,
		recovered_records=None):
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
	for jf in session_files(sdir, session_id):
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
				parent = (d.get("logicalParentUuid")
					if d.get("type") == "system"
					and d.get("subtype") == "compact_boundary"
					else d.get("parentUuid"))
				link.setdefault(u, parent)
				if is_node(d):
					nodes.setdefault(u, d)
	if recovered_records:
		for d in recovered_records:
			u = d.get("uuid")
			if not u:
				continue
			# The recovered copy comes from the source lineage. It carries the
			# authoritative parent link when a continuation copied this UUID.
			link[u] = (d.get("logicalParentUuid")
				if d.get("type") == "system"
				and d.get("subtype") == "compact_boundary"
				else d.get("parentUuid"))
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


def render_rails(order, parent_of, label_of, deco_of=None) -> list[str]:
	"""Lay out nodes (already in newest-first, child-before-parent order) as a
	`git log --graph`-style rail diagram. Each node is one `*` row; a node's lane
	stays open (`|`) until its parent appears below, where lanes converge (`|/`).
	Nodes sharing no history run in parallel lanes, like independent branches.

	`deco_of(nid)`, if given and truthy, prints an extra `◆` row just above the
	node in the same lane — a synthetic label node (used to hang a thread's title
	above its tip, so the title reads on its own line instead of crowding it)."""
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

		# Synthetic label row (e.g. a thread title) hung above the node row.
		deco = deco_of(nid) if deco_of else None
		if deco:
			row = [" "] * (2 * max(active) + 1)
			for c in active:
				row[2 * c] = "|"
			row[2 * mycol] = "◆"
			lines.append(f"{''.join(row).rstrip()} {deco}")

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


def analyze_graph(sdir: Path, full: bool = False, session_id=None,
		view=None, thinking=False) -> dict:
	"""Shared analysis behind every graph view. Builds the message DAG (only
	human prompts unless `full`), orders it newest-first / child-before-parent,
	and returns per-node helpers: `leaf_sid` (the resumable session id of the tip
	whose lane a node sits on), `title_for`, `gist_of`, plus `child_count`/`order`.

	`leaf_sid` is derived, not read off the record: forks rewrite sessionId on
	copied messages, so a shared node's own id is unreliable; instead each node is
	attributed to its newest descendant tip — the lane the graph draws it on — and
	a tip lives in one file only, so its sessionId is sound."""
	predicate = None if full else is_prompt
	if view is not None:
		predicate = lambda rec: visible_record(rec, view, thinking) is not None
	recovered = []
	sessions = load_sessions(sdir, session_id, recovered_ancestors=recovered)
	nodes, parent_of = build_message_graph(
		sdir, predicate, session_id, recovered_records=recovered)
	if view is not None:
		nodes = {uuid: visible_record(rec, view, thinking) for uuid, rec in nodes.items()}

	custom, ai = load_titles(sdir, session_id)
	opening = {sid: session_title(recs) for sid, _jf, recs, _ in sessions}

	def title_for(sid):
		return custom.get(sid) or ai.get(sid) or opening.get(sid, "")

	def pof(u):
		return parent_of.get(u)

	def ts_of(u):
		return nodes[u].get("timestamp") or ""

	order = graph_order(list(nodes), pof, ts_of)

	child_count = {u: 0 for u in nodes}
	for u in nodes:
		if pof(u) in child_count:
			child_count[pof(u)] += 1
	owner, pending = {}, {}
	for u in order:
		own = pending.pop(u, u)  # claimed by its newest child, else u is a tip itself
		owner[u] = own
		p = pof(u)
		if p is not None and p not in pending:
			pending[p] = own

	def leaf_sid(u):
		return nodes[owner[u]].get("sessionId") or owner[u]

	def gist_of(u):
		return msg_oneline(nodes[u]) if full or view == "conversation" else prompt_text(nodes[u])

	return {
		"nodes": nodes, "pof": pof, "ts_of": ts_of, "order": order,
		"child_count": child_count, "leaf_sid": leaf_sid,
		"title_for": title_for, "gist_of": gist_of, "full": full,
	}


def print_graph(sdir: Path, full: bool = False, session_id=None):
	"""Render the project's message DAG as a `git log --graph`-style oneline log.

	Two zoom levels on the same graph, picked by `full`:

	- default (navigate zoom): one row per prompt you actually typed — the intent
	  skeleton across every thread. Assistant/tool/thinking noise is dropped, but
	  the fork structure is preserved exactly, because you only ever fork *at* a
	  prompt: two threads share an identical typed prefix and then diverge on the
	  line where you said something different, so you recognise the split by your
	  own words. Parent links hop over the dropped messages.
	- full (inspect zoom): one row per message, the complete topology."""
	g = analyze_graph(sdir, full, session_id)
	nodes = g["nodes"]
	if not nodes:
		return
	pof, ts_of, order = g["pof"], g["ts_of"], g["order"]
	child_count, leaf_sid = g["child_count"], g["leaf_sid"]
	title_for, gist_of = g["title_for"], g["gist_of"]

	def redundant(title, gist):
		# True when the title is just the tip's own prompt (single-prompt thread),
		# differing only by truncation — no point showing it twice.
		a, b = title.rstrip("… "), gist.rstrip("… ")
		return a.startswith(b) or b.startswith(a)

	def label_of(u):
		t = ts_of(u)[5:16].replace("T", " ")  # MM-DD HH:MM
		return f"{short(leaf_sid(u))} [{t}] {gist_of(u)}"

	def deco_of(u):
		# Hang the thread's title on its own ◆ node above each tip.
		if child_count[u] != 0:
			return None
		title = title_for(leaf_sid(u))
		if not title or redundant(title, gist_of(u)):
			return None
		return f"«{title}»"

	print("\n".join(render_rails(order, pof, label_of, deco_of)))


def layout_rails(order, parent_of):
	"""Assign each node a (row, col) on the same lanes render_rails uses, but as
	coordinates rather than ASCII. Returns (pos: nid -> (row, col), maxcol)."""
	lanes = []
	pos = {}
	maxcol = 0
	for row, nid in enumerate(order):
		hits = [c for c, l in enumerate(lanes) if l == nid]
		if hits:
			mycol, extra = hits[0], hits[1:]
		else:
			mycol = next((c for c, l in enumerate(lanes) if l is None), len(lanes))
			if mycol == len(lanes):
				lanes.append(nid)
			else:
				lanes[mycol] = nid
			extra = []
		for c in extra:
			lanes[c] = None
		pos[nid] = (row, mycol)
		maxcol = max(maxcol, mycol)
		lanes[mycol] = parent_of(nid)
		while lanes and lanes[-1] is None:
			lanes.pop()
	return pos, maxcol


HTML_HEAD = """<!doctype html><html><head><meta charset="utf-8">
<title>cc_sessions graph</title><style>
body{margin:0;background:#0d1117;color:#c9d1d9;
 font:13px/1.4 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;}
header{position:sticky;top:0;z-index:5;background:#161b22;padding:8px 14px;
 border-bottom:1px solid #30363d;}
#filters{padding:8px 14px;background:#161b22;display:flex;gap:12px;flex-wrap:wrap;}
#filters select,#filters button{font:inherit;background:#0d1117;color:#c9d1d9;
 border:1px solid #30363d;border-radius:4px;padding:3px;max-width:100%;}
header b{color:#e6edf3;} header span{color:#8b949e;}
.row{cursor:pointer;}
.row .hl{fill:#ffffff;opacity:0;}
.row:hover .hl{opacity:.05;}
.sid{fill:#6e7681;} .time{fill:#586069;} .msg{fill:#c9d1d9;}
.row .sid:hover{fill:#58a6ff;text-decoration:underline;}
.title{font-weight:700;}
#toast{position:fixed;bottom:18px;left:50%;transform:translateX(-50%);z-index:30;
 background:#238636;color:#fff;padding:6px 12px;border-radius:6px;
 opacity:0;transition:opacity .2s;pointer-events:none;}
#reader{position:fixed;inset:0;z-index:20;background:rgba(1,4,9,.72);display:none;
 overflow-y:auto;padding:32px 16px;}
#reader.open{display:block;}
#pane{max-width:920px;margin:0 auto;background:#161b22;border:1px solid #30363d;
 border-radius:10px;box-shadow:0 12px 40px rgba(0,0,0,.5);}
#pane .top{position:sticky;top:-32px;display:flex;gap:10px;align-items:baseline;
 padding:12px 18px;background:#161b22;border-bottom:1px solid #30363d;
 border-radius:10px 10px 0 0;}
#pane .top .role{font-weight:700;text-transform:uppercase;letter-spacing:.05em;}
#pane .top .meta{color:#8b949e;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
#pane .top button{background:none;border:1px solid #30363d;color:#c9d1d9;border-radius:6px;
 cursor:pointer;font:inherit;padding:2px 9px;}
#pane .top button:hover{border-color:#8b949e;}
#body{padding:6px 22px 22px;font:15px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif;
 color:#e6edf3;overflow-wrap:anywhere;}
#body .blk{margin:16px 0;}
#body .lbl{font:600 12px ui-monospace,monospace;color:#8b949e;margin:0 0 4px;}
#body pre{background:#0d1117;border:1px solid #30363d;border-radius:6px;padding:10px 12px;
 overflow-x:auto;white-space:pre-wrap;tab-size:4;font:13px/1.45 ui-monospace,SFMono-Regular,Menlo,monospace;
 margin:6px 0;}
#body code{font:13px ui-monospace,SFMono-Regular,Menlo,monospace;background:#2d333b;
 padding:1px 5px;border-radius:4px;}
#body pre code{background:none;padding:0;}
#body h1,#body h2,#body h3,#body h4{margin:18px 0 6px;line-height:1.3;}
#body h1{font-size:1.4em;} #body h2{font-size:1.25em;} #body h3{font-size:1.1em;}
#body p{margin:8px 0;} #body ul,#body ol{margin:6px 0;padding-left:26px;}
#body blockquote{margin:8px 0;padding:0 12px;border-left:3px solid #30363d;color:#8b949e;}
#body table{border-collapse:collapse;margin:8px 0;font-size:14px;}
#body th,#body td{border:1px solid #30363d;padding:4px 9px;text-align:left;}
#body th{background:#1c2128;}
#body a{color:#58a6ff;}
#body hr{border:0;border-top:1px solid #30363d;}
#body .tool{border-left:3px solid #d29922;padding-left:12px;}
#body .res{border-left:3px solid #3fb950;padding-left:12px;}
#body .res.err{border-left-color:#f85149;}
#body .think,#body .sys{border-left:3px solid #6e7681;padding-left:12px;color:#8b949e;}
#body details>summary{cursor:pointer;color:#8b949e;font:12px ui-monospace,monospace;}
#body .kv{display:flex;gap:8px;align-items:baseline;}
#body .kv .k{color:#8b949e;font:12px ui-monospace,monospace;min-width:7em;}
</style></head><body>
"""

HTML_TAIL = """<div id="toast"></div>
<div id="reader"><div id="pane"><div class="top"><span class="role"></span>
<span class="meta"></span><button id="copy" title="copy claude --resume">resume</button>
<button id="close" title="close (Esc)">✕</button></div><div id="body"></div></div></div>
<script>
const embedded = (() => { const e = document.getElementById('msgs');
  return e ? JSON.parse(e.textContent) : null; })();
const filters = document.getElementById('filters');
if (filters) filters.addEventListener('change', () => filters.requestSubmit());
const toast = document.getElementById('toast');
function copy(cmd) {
  navigator.clipboard && navigator.clipboard.writeText(cmd);
  toast.textContent = 'copied: ' + cmd; toast.style.opacity = 1;
  setTimeout(() => { toast.style.opacity = 0; }, 1600);
}

// Minimal markdown: escape everything first, then add a safe subset of markup,
// so HTML quoted in a transcript can never execute or break the page.
function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;')
  .replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
function inline(s) {
  const codes = [];
  s = esc(s).replace(/`([^`]+)`/g, (m, c) => '\\x00' + (codes.push(c) - 1) + '\\x00');
  s = s.replace(/\\*\\*(.+?)\\*\\*/g, '<b>$1</b>')
    .replace(/(^|[^*\\w])\\*(?!\\s)([^*]+?)\\*(?!\\w)/g, '$1<i>$2</i>')
    .replace(/\\[([^\\]]+)\\]\\((https?:[^)\\s]+)\\)/g,
      '<a href="$2" target="_blank" rel="noopener">$1</a>');
  return s.replace(/\\x00(\\d+)\\x00/g, (m, i) => '<code>' + codes[i] + '</code>');
}
const FENCE = /^\\s*(```+|~~~+)/, HEAD = /^(#{1,6})\\s+(.*)/, ITEM = /^(\\s*)([-*+]|\\d+[.)])\\s+(.*)/;
const HR = /^\\s*([-*_])(\\s*\\1){2,}\\s*$/, TROW = /^\\s*\\|.*\\|\\s*$/, TSEP = /^\\s*\\|?\\s*:?-+:?\\s*(\\|\\s*:?-+:?\\s*)*\\|?\\s*$/;
function md(src) {
  const L = src.replace(/\\r/g, '').split('\\n'), out = [];
  let i = 0, m;
  const starts = l => FENCE.test(l) || HEAD.test(l) || HR.test(l) || ITEM.test(l)
    || /^\\s*>/.test(l) || TROW.test(l);
  const kind = im => /\\d/.test(im[2]) ? 'ol' : 'ul';
  while (i < L.length) {
    const l = L[i];
    if (!l.trim()) { i++; continue; }
    if ((m = l.match(FENCE))) {
      const buf = []; i++;
      while (i < L.length && !L[i].trim().startsWith(m[1])) buf.push(L[i++]);
      i++; out.push('<pre><code>' + esc(buf.join('\\n')) + '</code></pre>');
    } else if ((m = l.match(HEAD))) {
      const n = m[1].length; out.push(`<h${n}>${inline(m[2])}</h${n}>`); i++;
    } else if (HR.test(l)) {
      out.push('<hr>'); i++;
    } else if (TROW.test(l) && i + 1 < L.length && TSEP.test(L[i + 1])) {
      const cells = r => r.trim().replace(/^\\||\\|$/g, '').split(/(?<!\\\\)\\|/)
        .map(c => inline(c.trim().replace(/\\\\\\|/g, '|')));
      let h = '<table><tr>' + cells(l).map(c => `<th>${c}</th>`).join('') + '</tr>';
      i += 2;
      while (i < L.length && TROW.test(L[i]))
        h += '<tr>' + cells(L[i++]).map(c => `<td>${c}</td>`).join('') + '</tr>';
      out.push(h + '</table>');
    } else if (/^\\s*>/.test(l)) {
      const buf = [];
      while (i < L.length && /^\\s*>/.test(L[i])) buf.push(L[i++].replace(/^\\s*>\\s?/, ''));
      out.push('<blockquote>' + md(buf.join('\\n')) + '</blockquote>');
    } else if ((m = l.match(ITEM))) {
      const tag = kind(m), items = [];
      while (i < L.length && L[i].trim() && !FENCE.test(L[i]) && !HEAD.test(L[i])) {
        const im = L[i].match(ITEM);
        if (im && !im[1] && kind(im) !== tag) break;  // bullets -> numbers: new list
        if (im) items.push([im[1].length, im[3]]);
        else items[items.length - 1][1] += '\\n' + L[i].trim();
        i++;
      }
      out.push(`<${tag}>` + items.map(([ind, t]) =>
        `<li style="margin-left:${ind * 0.5}em">${t.split('\\n').map(inline).join('<br>')}</li>`)
        .join('') + `</${tag}>`);
    } else {
      const buf = [l]; i++;
      while (i < L.length && L[i].trim() && !starts(L[i])) buf.push(L[i++]);
      out.push('<p>' + buf.map(inline).join('<br>') + '</p>');
    }
  }
  return out.join('');
}

function pre(t) { return '<pre>' + esc(t) + '</pre>'; }
function fold(label, inner, open) {
  return `<details${open ? ' open' : ''}><summary>${esc(label)}</summary>${inner}</details>`;
}
function renderBlock(b) {
  if (b.type === 'text') {
    const t = b.text.trim();
    // System reminders, command wrappers etc.: tucked away, shown verbatim.
    if (t.startsWith('<')) return `<div class="blk sys">${fold(t.split('\\n')[0].slice(0, 80),
      pre(t), false)}</div>`;
    return `<div class="blk">${md(b.text)}</div>`;
  }
  if (b.type === 'thinking')
    return `<div class="blk think">${fold('thinking', md(b.text), false)}</div>`;
  if (b.type === 'tool_use') {
    const fields = Object.entries(b.input || {}).map(([k, v]) => {
      if (typeof v !== 'object' && !String(v).includes('\\n') && String(v).length < 100)
        return `<div class="kv"><span class="k">${esc(k)}</span><code>${esc(v)}</code></div>`;
      return `<div class="lbl">${esc(k)}</div>` +
        pre(typeof v === 'string' ? v : JSON.stringify(v, null, 2));
    }).join('');
    return `<div class="blk tool"><div class="lbl">⚙ ${esc(b.name)}</div>${fields}</div>`;
  }
  if (b.type === 'tool_result') {
    const n = b.text.split('\\n').length;
    const label = `↩ ${b.is_error ? 'error' : 'result'} · ${n} line${n === 1 ? '' : 's'}`;
    return `<div class="blk res${b.is_error ? ' err' : ''}">${fold(label, pre(b.text), n <= 40)}</div>`;
  }
  return `<div class="blk">${pre(b.text)}</div>`;
}

const reader = document.getElementById('reader'), body = document.getElementById('body');
let current = null;
async function openMsg(row) {
  const uuid = row.getAttribute('data-uuid');
  current = row.getAttribute('data-resume');
  reader.querySelector('.meta').textContent = '';
  reader.querySelector('.role').textContent = '…';
  body.innerHTML = '';
  reader.classList.add('open'); reader.scrollTop = 0;
  let m;
  try {
    m = embedded ? embedded[uuid] : await (await fetch('msg/' + uuid + location.search)).json();
  } catch (e) { m = null; }
  if (!m) { body.innerHTML = '<p>could not load message ' + esc(uuid) + '</p>'; return; }
  reader.querySelector('.role').textContent = m.role;
  reader.querySelector('.meta').textContent = [m.timestamp.replace('T', ' ').slice(0, 19),
    current.split(' ').pop(), m.model].filter(Boolean).join(' · ');
  body.innerHTML = m.blocks.map(renderBlock).join('') || '<p><i>(empty)</i></p>';
}
function closeReader() { reader.classList.remove('open'); }
document.getElementById('close').onclick = closeReader;
document.getElementById('copy').onclick = () => current && copy(current);
reader.addEventListener('click', e => { if (e.target === reader) closeReader(); });
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeReader(); });

for (const r of document.querySelectorAll('.row')) {
  r.addEventListener('click', e => {
    // The session hash copies the resume command; the rest of a message row
    // opens it in the reader. Title rows have no message, so they just copy.
    if (!r.hasAttribute('data-uuid') || e.target.closest('.sid'))
      copy(r.getAttribute('data-resume'));
    else openMsg(r);
  });
}
</script></body></html>
"""


def build_html(sdir: Path, full: bool = False, embed: bool = True,
		session_id=None, view=None, thinking=False):
	"""Build an interactive HTML/SVG of the message DAG: gitk-style lanes on the
	left, one row per node coloured by session, each thread tip with a ◆ title
	node, hover for the full prompt. Clicking a row's session hash copies its
	`claude --resume <id>` command; clicking the rest opens the message in a
	formatted reader pane. With `embed` every message's content is inlined so the
	file is self-contained; without it the page fetches `msg/<uuid>` on demand
	(what --serve does, keeping big projects' pages light). Returns the HTML
	string, or None if there are none."""
	view = view or ("all" if full else "prompts")
	full = view == "all"
	g = analyze_graph(sdir, full, session_id, view, thinking)
	nodes = g["nodes"]
	if not nodes and embed:
		return None
	pof, ts_of, order = g["pof"], g["ts_of"], g["order"]
	child_count, leaf_sid = g["child_count"], g["leaf_sid"]
	title_for, gist_of = g["title_for"], g["gist_of"]

	pos, maxcol = layout_rails(order, pof)

	ROW_H, COL_W, LPAD, TOP, CHARPX = 22, 16, 14, 10, 7.2

	def color(sid):
		return f"hsl({sum(sid.encode()) % 360}, 60%, 64%)"

	def cx(col):
		return LPAD + col * COL_W

	def cy(row):
		return TOP + row * ROW_H + ROW_H // 2

	def full_text(nid, limit=4000):
		# The whole message for the hover tooltip (not the truncated row gist):
		# the complete typed prompt, or in --full mode the expanded message.
		rec = nodes[nid]
		if view != "prompts":
			t = message_text(rec)
		else:
			t = "\n".join(x for x in _user_texts(rec) if x.strip()) or message_text(rec)
		t = t.strip()
		return t[:limit] + ("…" if len(t) > limit else "")

	# Weave a synthetic title node in just above each titled tip, so the topic
	# reads as its own ◆ node and the real leaf below shows only its last message.
	cols = {nid: c for nid, (_r, c) in pos.items()}

	def tip_title(nid):
		if child_count[nid] != 0:
			return ""
		t = title_for(leaf_sid(nid))
		return t if (t and t.rstrip("… ") not in gist_of(nid)) else ""

	display = []  # (kind, nid); a "title" entry sits immediately above its "node"
	for nid in order:
		if tip_title(nid):
			display.append(("title", nid))
		display.append(("node", nid))
	realrow = {nid: i for i, (kind, nid) in enumerate(display) if kind == "node"}

	# Edges (behind nodes): a smooth bezier from each node down to its parent.
	edges = []
	for nid in order:
		p = pof(nid)
		if p in realrow:
			x1, y1 = cx(cols[nid]), cy(realrow[nid])
			x2, y2 = cx(cols[p]), cy(realrow[p])
			ym = (y1 + y2) / 2
			edges.append(
				f'<path d="M{x1},{y1} C{x1},{ym} {x2},{ym} {x2},{y2}" '
				f'stroke="{color(leaf_sid(nid))}" fill="none" stroke-width="1.5" opacity=".6"/>')

	text_x = cx(maxcol) + 18
	rows, widest = [], 0
	for i, (kind, nid) in enumerate(display):
		c, sid = cols[nid], leaf_sid(nid)
		col, x, y = color(sid), cx(cols[nid]), cy(i)
		hl = f'<rect class="hl" x="0" y="{TOP + i * ROW_H}" width="100%" height="{ROW_H}"/>'
		resume = f'claude --resume {esc(sid)}'
		if kind == "title":
			title = title_for(sid)
			d = 5  # a diamond marker, with a short stem down to its tip
			diamond = (f'<path d="M{x},{y - d} L{x + d},{y} L{x},{y + d} L{x - d},{y} Z" '
				f'fill="{col}"/>')
			stem = (f'<line x1="{x}" y1="{y}" x2="{x}" y2="{cy(i + 1)}" '
				f'stroke="{col}" stroke-width="1.5" opacity=".6"/>')
			body = (f'{hl}{stem}{diamond}<text x="{text_x}" y="{y + 4}">'
				f'<tspan class="title" fill="{col}">«{esc(title)}»</tspan></text>')
			tooltip = title
			widest = max(widest, len(title) + 4)
		else:
			tstr = ts_of(nid)[5:16].replace("T", " ")
			gist = gist_of(nid)
			circle = f'<circle cx="{x}" cy="{y}" r="5" fill="{col}" stroke="#0d1117" stroke-width="1.5"/>'
			body = (f'{hl}{circle}<text x="{text_x}" y="{y + 4}">'
				f'<tspan class="sid">{esc(short(sid))}</tspan> '
				f'<tspan class="time">[{esc(tstr)}]</tspan>  '
				f'<tspan class="msg">{esc(gist)}</tspan></text>')
			tooltip = full_text(nid)
			widest = max(widest, len(short(sid)) + len(tstr) + len(gist) + 10)
		uuid_attr = f' data-uuid="{esc(nid)}"' if kind == "node" else ""
		rows.append(f'<g class="row" data-resume="{resume}"{uuid_attr}>'
			f'<title>{esc(tooltip)}</title>{body}</g>')

	width = int(text_x + widest * CHARPX + 30)
	height = TOP * 2 + len(display) * ROW_H
	svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
		f'font-family="inherit" font-size="13">'
		f'<g class="edges">{"".join(edges)}</g>'
		f'<g class="nodes">{"".join(rows)}</g></svg>')

	mode = {"all": "every message", "conversation": "prompts + answers",
		"prompts": "your prompts"}[view]
	header = (f'<header><b>cc_sessions</b> · {esc(sdir.name)} · {len(order)} nodes '
		f'({mode}) · <span>click a message to read it in full, click its session '
		f'hash to copy <b>claude --resume</b></span></header>')
	if not embed:
		options = "".join(
			f'<option value="{value}"{" selected" if value == view else ""}>{label}</option>'
			for value, label in (("prompts", "Prompts"),
				("conversation", "Prompts + answers"), ("all", "Everything")))
		selected = session_files(sdir, session_id)[0].stem if session_id else ""
		session_options = '<option value="">All sessions</option>' + "".join(
			f'<option value="{esc(jf.stem)}"'
			f'{" selected" if jf.stem == selected else ""}>{esc(jf.stem)}</option>'
			for jf in session_files(sdir))
		header += (f'<form id="filters" method="get"><label>Show <select name="view">'
			f'{options}</select></label> <label>Session <select name="id">'
			f'{session_options}</select></label> <label><input type="checkbox" '
			f'name="thinking" value="1"{" checked" if thinking else ""}> '
			'Thinking (Everything)</label>'
			'<input type="hidden" name="filters" value="1"> '
			'<button type="submit">Refresh</button></form>')
		if not nodes:
			header += '<p>No messages match these filters. Try Everything or another session.</p>'
	data = ""
	if embed:
		# `</` escaped so message text can't close the <script> element early.
		payload = json.dumps({u: message_payload(nodes[u]) for u in order},
			ensure_ascii=False).replace("</", "<\\/")
		data = f'<script id="msgs" type="application/json">{payload}</script>'
	return HTML_HEAD + header + svg + data + HTML_TAIL


def print_html(sdir: Path, full: bool = False, out_path: str = None,
		session_id=None, view=None, thinking=False) -> int:
	"""Build the interactive HTML/SVG graph and write it to a file."""
	html = build_html(sdir, full, session_id=session_id, view=view, thinking=thinking)
	if html is None:
		print("error: no messages to render", file=sys.stderr)
		return 1
	out = Path(out_path).expanduser()
	out.write_text(html, encoding="utf-8")
	print(f"Wrote {out}")
	print(f"Open it:  xdg-open {out}")
	return 0


def serve_html(sdir: Path, full: bool = False, port: int = 8000,
		session_id=None, view=None, thinking=False) -> int:
	"""Serve the interactive graph over HTTP, regenerated on every request so a
	browser refresh reflects newly-written messages. Binds to localhost only;
	Ctrl-C to stop. If the requested port is taken, falls back to a free one."""
	import http.server
	import webbrowser

	default_view = view or ("all" if full else "prompts")

	class Handler(http.server.BaseHTTPRequestHandler):
		def do_GET(self):
			request = urlsplit(self.path)
			path = request.path
			query = parse_qs(request.query, keep_blank_values=True)
			active_view = query.get("view", [default_view])[0]
			active_id = query.get("id", [session_id])[0] or None
			active_thinking = query.get("thinking", [
				"0" if "filters" in query else "1" if thinking else "0"])[0] == "1"
			try:
				if active_view not in ("prompts", "conversation", "all"):
					raise ValueError("invalid view")
				session_files(sdir, active_id)
			except ValueError as error:
				self.send_error(400, str(error))
				return
			if path.startswith("/msg/"):
				# Reader pane content, looked up fresh across every message
				# (not just the graph's nodes) so it works in either zoom.
				recovered = []
				load_sessions(sdir, active_id, recovered_ancestors=recovered)
				nodes, _ = build_message_graph(
					sdir, session_id=active_id, recovered_records=recovered)
				rec = nodes.get(path[len("/msg/"):])
				if rec is not None:
					rec = visible_record(rec, active_view, active_thinking)
				if rec is None:
					self.send_error(404, "no such message")
					return
				body = json.dumps(message_payload(rec), ensure_ascii=False).encode("utf-8")
				ctype = "application/json"
			elif path in ("/", "/index.html"):
				html = build_html(sdir, full, embed=False, session_id=active_id,
					view=active_view, thinking=active_thinking)
				if html is None:
					self.send_error(404, "no messages to render")
					return
				body = html.encode("utf-8")
				ctype = "text/html; charset=utf-8"
			else:
				self.send_error(404)
				return
			self.send_response(200)
			self.send_header("Content-Type", ctype)
			self.send_header("Content-Length", str(len(body)))
			self.send_header("Cache-Control", "no-store")
			self.end_headers()
			self.wfile.write(body)

		def log_message(self, *args):  # keep the terminal quiet
			pass

	try:
		httpd = http.server.HTTPServer(("127.0.0.1", port), Handler)
	except OSError:
		httpd = http.server.HTTPServer(("127.0.0.1", 0), Handler)  # port busy -> any free port
	url = f"http://127.0.0.1:{httpd.server_address[1]}/"
	mode = default_view
	print(f"Serving cc_sessions graph ({mode}) for {sdir.name} at {url}")
	print("  refresh the page to pick up new messages · Ctrl-C to stop")
	if os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
		try:
			webbrowser.open(url)
		except Exception:
			pass
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		print("\nstopped")
	finally:
		httpd.server_close()
	return 0


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


def message_payload(rec) -> dict:
	"""JSON-able view of one message for the HTML reader pane: metadata plus its
	content blocks, kept structured (not flattened) so the browser can format
	prose as markdown, tool inputs field by field and tool output verbatim."""
	msg = rec.get("message", {})
	content = msg.get("content")
	if isinstance(content, str):
		content = [{"type": "text", "text": content}]
	blocks = []
	for b in content or []:
		bt = b.get("type", "?")
		if bt == "text":
			blocks.append({"type": "text", "text": b.get("text") or ""})
		elif bt == "thinking":
			# Often redacted to "" on disk; say so rather than show nothing.
			text = b.get("thinking") or ""
			blocks.append({"type": "thinking",
				"text": text if text.strip() else "*(not recorded in the transcript)*"})
		elif bt == "tool_use":
			blocks.append({"type": "tool_use", "name": b.get("name", "?"),
				"input": b.get("input", {})})
		elif bt == "tool_result":
			blocks.append({"type": "tool_result", "text": tool_result_text(b.get("content")),
				"is_error": bool(b.get("is_error"))})
		elif bt == "image":
			blocks.append({"type": "other", "text": "[image]"})
		else:
			blocks.append({"type": "other", "text": json.dumps(b, ensure_ascii=False)[:2000]})
	return {
		"role": msg.get("role") or rec.get("type") or "?",
		"timestamp": rec.get("timestamp") or "",
		"uuid": rec.get("uuid") or "",
		"model": msg.get("model") or "",
		"blocks": blocks,
	}


def export_git(sdir: Path, outdir: str, full: bool = False, force: bool = False,
		session_id=None) -> int:
	"""Materialise the message DAG as a throwaway git repo so it can be browsed
	with any git history GUI (gitk, git gui, tig, lazygit, VS Code Git Graph…).

	Each node becomes a commit (parentUuid -> git parent, message timestamp ->
	commit date), the session id is sneaked into both the commit subject and a
	`sess/<id>` branch at that session's tip, and the message body is written to
	`msg/<uuid>.md` so the GUI's diff/patch pane shows the message itself. By
	default one commit per user prompt; full=True commits every message."""
	nodes, parent_of = build_message_graph(sdir, None if full else is_prompt, session_id)
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
		# --force allows non-fast-forward ref moves when refreshing an existing
		# export (e.g. switching between prompt-only and --full rebuilds main).
		["git", "-C", str(out), "fast-import", "--quiet", "--force", "--date-format=raw"],
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
	ap.add_argument("--id", metavar="SESSION_ID",
		help="Select one session by full ID or unique prefix (includes its copied history)")
	ap.add_argument("--view", choices=("prompts", "conversation", "all"),
		help="Initial --serve/--html view: prompts, prompts + answers, or everything")
	ap.add_argument("--full", action="store_true",
		help="Show full detail: untruncated tool inputs/results in the dump; "
			"every message in --tree, --git-export, --html and --serve")
	ap.add_argument("--thinking", action="store_true",
		help="Show assistant thinking blocks, including in --serve/--html")
	ap.add_argument("--list", action="store_true",
		help="Just list sessions found and exit")
	ap.add_argument("--tree", action="store_true",
		help="Show the message DAG as a git-log-graph oneline log (just your "
			"prompts; add --full for every message) and exit")
	ap.add_argument("--git-export", nargs="?", const="", default=None, metavar="DIR",
		help="Export the message DAG as a throwaway git repo for browsing with gitk "
			"--all; omit DIR to use ~/.cache/cc_sessions/<project> (auto-refreshed)")
	ap.add_argument("--html", nargs="?", const="", default=None, metavar="FILE",
		help="Write an interactive HTML/SVG graph (gitk-style, click to copy "
			"--resume); omit FILE to use ~/.cache/cc_sessions/<project>.html")
	ap.add_argument("--serve", nargs="?", const=8000, default=None, type=int, metavar="PORT",
		help="Serve the interactive graph on http://localhost:PORT (default 8000), "
			"regenerated each request so a refresh shows new messages")
	ap.add_argument("--force", action="store_true",
		help="With --git-export: allow reusing a non-empty target directory")
	args = ap.parse_args()

	try:
		sdir = resolve_sessions_dir(args.path)
		session_files(sdir, args.id)
	except (FileNotFoundError, ValueError) as e:
		print(f"error: {e}", file=sys.stderr)
		return 2

	if args.git_export is not None:
		auto = args.git_export == ""
		target = Path.home() / ".cache" / "cc_sessions" / sdir.name if auto else args.git_export
		# The auto cache path is ours to manage, so refresh it in place.
		return export_git(sdir, str(target), args.full, args.force or auto, args.id)

	if args.html is not None:
		if args.html == "":
			cache = Path.home() / ".cache" / "cc_sessions"
			cache.mkdir(parents=True, exist_ok=True)
			out = cache / f"{sdir.name}.html"
		else:
			out = args.html
		return print_html(sdir, args.full, str(out), args.id, args.view, args.thinking)

	if args.serve is not None:
		return serve_html(sdir, args.full, args.serve, args.id, args.view, args.thinking)

	recovery_warnings = []
	sessions = load_sessions(sdir, args.id, recovery_warnings)
	if not sessions:
		print(f"(no conversational records in {sdir})", file=sys.stderr)
		return 1
	for warning in recovery_warnings:
		kind = "info" if warning.startswith("INFO: ") else "warning"
		message = warning.removeprefix("INFO: ")
		stream = sys.stdout if kind == "info" else sys.stderr
		print(f"{kind}: {message.replace(chr(10), chr(10) + '  ')}", file=stream)

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
		print_graph(sdir, args.full, args.id)
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
