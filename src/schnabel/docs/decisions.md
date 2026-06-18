# Decisions log

Append-only record. When a decision is reversed, a new entry supersedes the old; we do not edit history. Each entry: question, alternatives, choice, why.

## D-001 — Connection descriptor format

- **Date:** 2026-05-20
- **Status:** Adopted
- **Question:** How is the quadstore connection configured (env var, file, command-line)?
- **Alternatives:**
  1. Per-key env vars (`SEMANTIC_DESKTOP_AGRAPH_HOST`, `_PORT`, `_GRAPH`, …) — extension by coordinated addition of new vars.
  2. Connection URL (`sparql+http://user:pass@host:port/repo?graph=...`) — familiar from postgres/redis; URI grammar for query params.
  3. JSON5 descriptor in a single env var `QUADSTORE`, with `@/path/to/file` escape hatch.
- **Choice:** Option 3.
- **Why:** The connection negotiation is itself a first-class concern that will evolve — adding pubsub backends, auth methods, role-keyed sub-descriptors, peer references. URL grammar is too rigid for nested structures; per-key env vars require coordinated additions for every new field. A JSON5 descriptor naturally accommodates extension; comments, trailing commas, and unquoted keys make it tolerable to hand-edit.

## D-002 — No upfront ontology

- **Date:** 2026-05-20
- **Status:** Adopted
- **Question:** Do we write a Turtle/RDFS ontology file first, then code against it; or define predicates inline in code and harvest a vocab document later?
- **Alternatives:**
  1. Upfront ontology — formal definitions of classes, predicates, ranges; code references them.
  2. Code-first — predicates live as constants in the emitting module; vocab doc generated periodically as documentation of the de-facto state.
- **Choice:** Code-first.
- **Why:** Upfront ontology design oscillates between the ontology and the code it constrains. The cost of being wrong upfront is shipped as friction every time we want to add a predicate. Predicates that earn their place by being emitted-and-consumed are the ones we want; predicates that exist only in the ontology bit-rot. See `prior-art.md` on Tracker3's per-connection graph policy — that's what an ontology *requirement* costs.

## D-003 — SPARQL 1.1 HTTP as wire protocol baseline

- **Date:** 2026-05-20
- **Status:** Adopted
- **Question:** What protocol does the EventLog speak to its backing store?
- **Alternatives:**
  1. Vendor-specific bindings (Franz SDK for AllegroGraph, libtracker for Tracker3, …).
  2. SPARQL 1.1 Protocol over HTTP — the lowest common multiple across stores.
  3. rdflib `Store` interface only, no remote.
- **Choice:** SPARQL 1.1 HTTP, accessed in Python through rdflib's `SPARQLUpdateStore`.
- **Why:** Pyin's `pymantic.sparql` was already protocol-agnostic; rdflib's stores generalize the same way. Speaking SPARQL means we get Fuseki, Oxigraph, Virtuoso, AllegroGraph, GraphDB, and Tracker3-HTTP-endpoint all behind one interface. Other languages get free interop via any HTTP client.

## D-004 — Pubsub via MQTT, not store-native notifications

- **Date:** 2026-05-20
- **Status:** Adopted (planned for phase 3; not in phase 1)
- **Question:** How do subscribers learn that new triples have landed in a graph they care about?
- **Alternatives:**
  1. Store-native (Tracker3 DBus signals, AllegroGraph SSE, …) — closest coupling, varies per store.
  2. SEPA (SPARQL queries as subscriptions over WebSockets) — academic, low maturity.
  3. MQTT broker as a sidecar; emit-side also publishes to a topic derived from the graph IRI.
  4. Polling cursor (high-water-mark timestamp).
- **Choice:** MQTT.
- **Why:** No widely-deployed open SPARQL store has a battle-tested pubsub. MQTT is the most-deployed pubsub on the planet, has mature ACL (Mosquitto's `acl_file`, EMQX's JWT), v5 supports `Content-Type` headers (`application/n-quads`) so payloads carry the actual delta. Decoupling pubsub from store means each can be picked best-of-breed. Polling is the v1 fallback when no broker is configured.

## D-005 — Drop Tracker3 from v1

- **Date:** 2026-05-20
- **Status:** Adopted (with caveats)
- **Question:** Should the first concrete backend be Tracker3 (already installed on GNOME, native DBus signals, per-graph ACL)?
- **Alternatives:**
  1. Yes — semantic-desktop-iest choice, gets us free pubsub and ACL.
  2. No — too much setup friction (per-connection graph policy, ontology requirement).
- **Choice:** No, for phase 1.
- **Why:** Tracker3 insists that every graph IRI written to must be pre-registered in the connection's graph policy. Our natural pattern is `urn:schnabel:graph:<fresh-uuid>_invocation` per run — a new graph per emit-burst. Working around this means either (a) one shared graph + invocation-as-predicate (denormalization), or (b) negotiating a wildcard graph policy that defeats the ACL premise. Neither is acceptable. Tracker3 remains a *possible future* backend for users who want it, but the design must not assume it. Plus: DBus signals are local-only, so it doesn't even solve cross-machine pubsub.

## D-006 — Graph-per-invocation as the canonical unit of activity

- **Date:** 2026-05-20
- **Status:** Adopted
- **Question:** How are an emitter's quads scoped within the store?
- **Alternatives:**
  1. All quads in one default graph, distinguished by an `emittedBy` predicate per triple.
  2. Each process invocation gets a fresh named graph; its triples live there.
  3. Hybrid — predicate when the burst is small, graph when large.
- **Choice:** Graph-per-invocation.
- **Why:** Using the quad's graph column for provenance costs one column we already paid for. Using a predicate means every triple becomes 2 triples — N% overhead at all times. Pyin's per-step graph naming demonstrates the pattern at much higher rates; we follow that lead. Bonuses: dropping a failed invocation = dropping a graph. Querying "this invocation's full state" = one graph IRI.

## D-007 — Multi-machine: each side sovereign, cross-machine via SSH + MQTT

- **Date:** 2026-05-20
- **Status:** Adopted (architectural goal; phase 4)
- **Question:** When the invoker is on one host and the invokee on another (e.g. a guest VM), how do they interoperate?
- **Alternatives:**
  1. Single shared store hosted on the "trusted" side; both sides write to it remotely.
  2. Each side runs its own store. Invokee publishes pubsub notifications the invoker can subscribe to; invoker queries invokee's SPARQL endpoint over HTTP with read-only credentials.
- **Choice:** Option 2.
- **Why:** Stronger isolation; each side controls what it accepts. Battle-tested layers do the heavy lifting: SSH for transport encryption + mutual auth + tunneling; MQTT broker for ACL'd notifications; SPARQL endpoint for read-only data access. No new ACL primitive to design or trust.

## D-008 — Project name: schnabel

- **Date:** 2026-05-20
- **Status:** Adopted (working name; trivial to rename later)
- **Question:** What do we call this thing?
- **Alternatives considered:** `semd`, `quadbus`, `agora`, `scribe`, `forum`, `soapbox`, `rostrum`, `stele`, `moot`, `bevan`, `truth`, `preacher`, `rewind`.
- **Choice:** `schnabel`.
- **Why:** German *Schnabel* = beak. Connects to *rostrum* (Latin beak, the Roman speaker's platform decorated with bronze ship-beaks). *Halt den Schnabel!* makes the speech-organ metaphor explicit. Distinct enough to grep, low namespace collision in software.

## D-010 — `invocation()` context manager as the canonical activity primitive

- **Date:** 2026-05-20
- **Status:** Adopted
- **Question:** Each emitter (bfg's `local_commit`, `push`, `pull`, etc.) needs the same 15-line lifecycle boilerplate: mint graph IRI, emit type + startedAt, swap latest-invocation pointer, do work, emit status+endedAt on exit, emit failed+error+endedAt on exception. Inline at each call site, or extract a helper?
- **Alternatives:**
  1. Inline at every call site — strictly follows D-002's "don't abstract early," each command is self-contained.
  2. Extract a `with log.invocation(BFG.X) as inv:` context manager that handles the lifecycle uniformly and yields a graph-scoped handle.
- **Choice:** Option 2.
- **Why:** Two repetitions (`local_commit` and `push`) were enough to make the boilerplate's tax — 15+ lines of `_log.batch()` / `_log.emit(...g=inv)` / failure-handling per command — obviously wasteful, with ~10 more commands queued. The helper doesn't anticipate hypothetical future requirements; it consolidates a pattern already proven in the codebase. It also encodes the canonical lifecycle vocabulary (`core:startedAt`, `core:endedAt`, `core:status`, `core:error`, `core:running`/`complete`/`failed`) so every emitter automatically agrees on those terms — cross-emitter SPARQL joins ("what was running at 14:32") work without per-tool translation.
- **Shape:** `_InvocationHandle` is the yielded object. Has `iri` (the graph IRI), `emit(p, o)` (emits in the invocation's graph with `s=iri`), `emit_about(s, p, o)` (graph-scoped but arbitrary subject — for child resources like snapshots the invocation produced), and `bn(suffix)` (mint a child-resource IRI). In null-mode `iri=None` and all methods short-circuit, so call sites stay unconditional.

## D-011 — Byte-count reporting goes to both sinks (schnabel **and** the file-tee'd log)

- **Date:** 2026-05-20
- **Status:** Adopted
- **Question:** When bfg's send pipeline reports byte progress, where does it land?
- **Alternatives:**
  1. Schnabel only — only consumers with a configured QUADSTORE see the numbers.
  2. The file-tee'd log only (the original prose stream) — preserves backward compatibility but the data isn't queryable.
  3. Both sinks. Same source, two materializations.
- **Choice:** Option 3.
- **Why:** The pyin lesson: a single emit call writing to two sinks (the `.n3` file *and* the SPARQL accumulator) is the proven shape, neither sink is privileged, and operators get to keep using `grep` on the tee'd log while machine consumers query SPARQL. For bfg specifically: anyone debugging a stalled backup will reach for the existing log first; removing the byte counts from there to force them to set up a QUADSTORE would be a regression in feature parity. The helper ``_emit_bytes_progress(invocation, n, kind)`` writes to both at one call site, so they can never drift.
- **Shape:**
  - `local_send` (shell pipeline with ssh receive or file redirect): inject `pv -nbf 2>$tmpfile` between `btrfs send` and the target. A daemon thread tails the tmpfile, throttles to ~one report per 64 MiB advance, and calls `_emit_bytes_progress`. Falls back to the original shell command (with a one-line warning) when `pv` isn't on `$PATH`.
  - `remote_send` (already a Popen chain): replace `p2.communicate()` with a hand-rolled read-from-p1-stdout / write-to-p2-stdin loop in 4-MiB chunks; emit progress at the same 64-MiB threshold.
  - Both paths emit a final value after the subprocess exits so we never drop the total.
  - Byte counts accumulate (one quad per threshold cross), not pointer-swap. The progress curve is itself an audit artifact. Consumers wanting "current" can ``MAX(?n)`` or ``ORDER BY DESC LIMIT 1``.

## D-009 — Packaging and install model

- **Date:** 2026-05-20
- **Status:** Adopted
- **Question:** How do consumers (bfg, hackery2) pick up schnabel during development, before it has an upstream release?
- **Alternatives:**
  1. Vendored copy in each consumer.
  2. PyPI release from day one.
  3. Editable path dependency in each consumer's existing package manifest.
- **Choice:** Option 3.
- **Why:** Vendoring duplicates code and diverges. PyPI is premature — the API is in flux. Editable path deps let edits to schnabel be picked up by all consumers immediately, and the eventual extract-to-its-own-repo step is just "publish + change the dep spec." Concrete shape:
  - schnabel itself is uv-managed (pyproject.toml + hatchling build backend; matches the user's "prefer uv where uncommitted" preference).
  - bfg (poetry-managed) declares the dep as `schnabel = {path = "../../../hackery2/dev/hackery2/src/schnabel", develop = true}`.
  - hackery2 (setuptools + pipx) cannot put a path dep in `setup.py` cleanly; instead `install.sh` runs `pipx runpip hackery2 install -e ./src/schnabel` after the main pipx install. This sidesteps `pipx inject`'s historical quirks with editable installs.
  - Both consumers get `rdflib` and `json5` transitively from schnabel; neither declares them directly.

---

(More decisions will land here as we make them.)
