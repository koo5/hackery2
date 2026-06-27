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
hover for the full prompt, click a row to copy its `claude --resume` command.
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


def esc(s) -> str:
	"""Escape text for embedding in HTML/SVG (element text and attributes)."""
	return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
		.replace('"', "&quot;"))


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


def load_titles(sdir: Path):
	"""Map session id -> (custom_title, ai_title) from the title records Claude
	Code writes: `/rename` appends a `custom-title` record and the auto-namer an
	`ai-title` record, both `{..., sessionId}`. Last write per session wins."""
	custom, ai = {}, {}
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


def analyze_graph(sdir: Path, full: bool = False) -> dict:
	"""Shared analysis behind every graph view. Builds the message DAG (only
	human prompts unless `full`), orders it newest-first / child-before-parent,
	and returns per-node helpers: `leaf_sid` (the resumable session id of the tip
	whose lane a node sits on), `title_for`, `gist_of`, plus `child_count`/`order`.

	`leaf_sid` is derived, not read off the record: forks rewrite sessionId on
	copied messages, so a shared node's own id is unreliable; instead each node is
	attributed to its newest descendant tip — the lane the graph draws it on — and
	a tip lives in one file only, so its sessionId is sound."""
	nodes, parent_of = build_message_graph(sdir, None if full else is_prompt)

	custom, ai = load_titles(sdir)
	opening = {sid: session_title(recs) for sid, _jf, recs, _ in load_sessions(sdir)}

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
		return msg_oneline(nodes[u]) if full else prompt_text(nodes[u])

	return {
		"nodes": nodes, "pof": pof, "ts_of": ts_of, "order": order,
		"child_count": child_count, "leaf_sid": leaf_sid,
		"title_for": title_for, "gist_of": gist_of, "full": full,
	}


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
	g = analyze_graph(sdir, full)
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
header b{color:#e6edf3;} header span{color:#8b949e;}
.row{cursor:pointer;}
.row .hl{fill:#ffffff;opacity:0;}
.row:hover .hl{opacity:.05;}
.sid{fill:#6e7681;} .time{fill:#586069;} .msg{fill:#c9d1d9;}
.title{font-weight:700;}
#toast{position:fixed;bottom:18px;left:50%;transform:translateX(-50%);
 background:#238636;color:#fff;padding:6px 12px;border-radius:6px;
 opacity:0;transition:opacity .2s;pointer-events:none;}
</style></head><body>
"""

HTML_TAIL = """<div id="toast"></div><script>
for (const r of document.querySelectorAll('.row')) {
  r.addEventListener('click', () => {
    const cmd = r.getAttribute('data-resume');
    navigator.clipboard && navigator.clipboard.writeText(cmd);
    const t = document.getElementById('toast');
    t.textContent = 'copied: ' + cmd; t.style.opacity = 1;
    setTimeout(() => { t.style.opacity = 0; }, 1600);
  });
}
</script></body></html>
"""


def print_html(sdir: Path, full: bool = False, out_path: str = None) -> int:
	"""Write the message DAG as a self-contained interactive HTML/SVG file:
	gitk-style lanes on the left, one row per node coloured by session, each
	thread tip badged with its title, hover for the full prompt, click a row to
	copy its `claude --resume <id>` command."""
	g = analyze_graph(sdir, full)
	nodes = g["nodes"]
	if not nodes:
		print("error: no messages to render", file=sys.stderr)
		return 1
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
			tooltip = gist
			widest = max(widest, len(short(sid)) + len(tstr) + len(gist) + 10)
		rows.append(f'<g class="row" data-resume="{resume}"><title>{esc(tooltip)}</title>{body}</g>')

	width = int(text_x + widest * CHARPX + 30)
	height = TOP * 2 + len(display) * ROW_H
	svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
		f'font-family="inherit" font-size="13">'
		f'<g class="edges">{"".join(edges)}</g>'
		f'<g class="nodes">{"".join(rows)}</g></svg>')

	mode = "every message" if full else "your prompts"
	header = (f'<header><b>cc_sessions</b> · {esc(sdir.name)} · {len(order)} nodes '
		f'({mode}) · <span>click a row to copy its <b>claude --resume</b> command, '
		f'hover for the full prompt</span></header>')
	html = HTML_HEAD + header + svg + HTML_TAIL

	out = Path(out_path).expanduser()
	out.write_text(html, encoding="utf-8")
	print(f"Wrote {out}  ({len(order)} nodes, {width}×{height}px)")
	print(f"Open it:  xdg-open {out}")
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


def export_git(sdir: Path, outdir: str, full: bool = False, force: bool = False) -> int:
	"""Materialise the message DAG as a throwaway git repo so it can be browsed
	with any git history GUI (gitk, git gui, tig, lazygit, VS Code Git Graph…).

	Each node becomes a commit (parentUuid -> git parent, message timestamp ->
	commit date), the session id is sneaked into both the commit subject and a
	`sess/<id>` branch at that session's tip, and the message body is written to
	`msg/<uuid>.md` so the GUI's diff/patch pane shows the message itself. By
	default one commit per user prompt; full=True commits every message."""
	nodes, parent_of = build_message_graph(sdir, None if full else is_prompt)
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
	ap.add_argument("--full", action="store_true",
		help="Show full detail: untruncated tool inputs/results in the dump; "
			"every message (not just prompts) in --tree and --git-export")
	ap.add_argument("--thinking", action="store_true",
		help="Show assistant thinking blocks")
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
	ap.add_argument("--force", action="store_true",
		help="With --git-export: allow reusing a non-empty target directory")
	args = ap.parse_args()

	try:
		sdir = resolve_sessions_dir(args.path)
	except FileNotFoundError as e:
		print(f"error: {e}", file=sys.stderr)
		return 2

	if args.git_export is not None:
		auto = args.git_export == ""
		target = Path.home() / ".cache" / "cc_sessions" / sdir.name if auto else args.git_export
		# The auto cache path is ours to manage, so refresh it in place.
		return export_git(sdir, str(target), args.full, args.force or auto)

	if args.html is not None:
		if args.html == "":
			cache = Path.home() / ".cache" / "cc_sessions"
			cache.mkdir(parents=True, exist_ok=True)
			out = cache / f"{sdir.name}.html"
		else:
			out = args.html
		return print_html(sdir, args.full, str(out))

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
