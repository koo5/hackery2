# Roadmap

Phased plan. Phase 0 is "before any of this exists"; each later phase requires the previous one.

## Phase 0 — Today

bfg emits via prose-on-stdout-mixed-with-one-JSON-line. backup.sh `tee`s the output and `grep`s for `{"result"`. Per-invocation logs don't exist (one concatenated stream). Parent snapshot is logged at DEBUG, never surfaced. Zero byte accounting.

## Phase 1 — `schnabel.EventLog` + minimum bfg wiring ✅

**Deliverables:**

- [x] `schnabel/events.py` with the API per [`design.md`](design.md).
- [x] `memory`, `nquads-file`, and `sparql-http` backends.
- [x] bfg's `local_commit` wired to emit invocation/snapshot quads.
- [x] `QUADSTORE` env var honored; null-mode when absent.
- [x] Editable-installed into bfg via poetry path dep; into hackery2 via `pipx runpip` in `install.sh` (D-009).

**Done.** Per-invocation traces land in any configured QUADSTORE; SPARQL retrieves them.

## Phase 2 — All bfg commands instrumented; backup.py reads back (in progress)

**Deliverables:**

- [x] `EventLog.invocation()` context manager extracted to handle the lifecycle pattern (D-010).
- [x] `local_commit` refactored onto the helper.
- [x] `push` emits invocation quads, including `bfg:parentSnapshot` (reified with abspath + uuids) when `find_common_parent` picks one (one of the original three asks).
- [x] `pull` emits the same structure symmetrically.
- [x] Byte counting plumbed into `local_send` (via `pv -nbf` injection + tmpfile-tailing daemon thread) and `remote_send` (in-process Popen chain with chunked read/write counter). Reports to both sinks: the existing `_prerr`/`tee`'d log AND the active schnabel invocation, as `bfg:bytesTransferred` quads at every 64 MiB threshold plus a final (D-011).
- [x] `remote_commit`, `checkout_local`, `checkout_remote`, `update_db`, `prune_local`, `prune_remote` emit. `prune_local`/`prune_remote` also emit one `bfg:prunedSnapshot` quad per deleted snapshot.
- [x] Compound commands (`commit_and_push`, `remote_commit_and_pull`, `commit_and_push_and_checkout`, `commit_and_generate_patch`) wrap their bodies in their own `log.invocation()`. Inner `local_commit`/`push`/`pull`/`checkout_*` invocations automatically link via `core:invokedBy` because `EventLog.invocation()` sets/restores `SCHNABEL_PARENT_INVOCATION` around its body (D-012a).
- [x] backup.py mints an outer invocation IRI per `_run_backup`; child bfg invocations record `core:invokedBy <outer>` via the `SCHNABEL_PARENT_INVOCATION` env var (D-012).
- [x] backup.py prints an end-of-run summary by querying the store for all child invocations (subvol, parent snapshot used, max bytes transferred, push/pull destination, status). Single SPARQL query; per-child Python-side formatting.

**Done when:** the three asks from the original conversation are met. Detailed per-invocation log via graph-per-invocation **(done)**; parent snapshot surfaced via emitted `bfg:parentSnapshot` **(done)**; byte accounting via emitted `bfg:bytesTransferred` **(done)**. All public bfg commands instrumented; all compound commands form proper call trees; backup.py's outer invocation links to children automatically. **Phase 2 complete.**

## Phase 3 — Pubsub: MQTT + `bfg-watch`

**Deliverables:**

- MQTT pubsub backend in EventLog (publishes on emit, subscribes via `subscribe()`).
- Mosquitto config sketch in docs.
- `bfg-watch` CLI: subscribes to all active invocations, renders a live TUI (subvols in flight, MB/s, ETA, parent snapshot, error tail).

**Done when:** a user can run `bfg-watch` in another terminal and see live progress as backups run.

## Phase 4 — Multi-machine

**Deliverables:**

- Cross-machine invocation linkage: when bfg on host A invokes a remote bfg over SSH, both write to their own local stores; both publish to the shared MQTT broker; the outer invocation graph references the inner one by IRI.
- Schnabel-aware SSH wrapper or convention: outer process passes its invocation IRI + broker creds to the remote invocation.
- SSH-tunnel deployment pattern documented (broker on which side, who connects to whom, recommended Mosquitto ACL templates).
- SPARQL-endpoint-exposure pattern documented (Fuseki on the guest, SSH-tunneled to the invoker).

**Done when:** an invoker on host can see, in realtime, what the invokee in a VM is doing, without trusting the invokee with write access to the invoker's store.

## Phase 5 — Other tools join the bus

**Deliverables:**

- `intention` (the dev-intention tracker) emits intention-change quads.
- `ccc_full` (the conversation tool) emits session-boundary quads.
- A `~/.local/state/schnabel/store.nq` or equivalent default catches everything for any tool that doesn't have a dedicated Fuseki dataset.
- A canonical SPARQL query — `WHAT_HAPPENED.sparql` — that returns a unified timeline across tools for a given day.

**Done when:** querying "what was happening on this host this hour" is one SPARQL away.
