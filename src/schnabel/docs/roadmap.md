# Roadmap

Phased plan. Phase 0 is "before any of this exists"; each later phase requires the previous one.

## Phase 0 — Today

bfg emits via prose-on-stdout-mixed-with-one-JSON-line. backup.sh `tee`s the output and `grep`s for `{"result"`. Per-invocation logs don't exist (one concatenated stream). Parent snapshot is logged at DEBUG, never surfaced. Zero byte accounting.

## Phase 1 — `schnabel.EventLog` + minimum bfg wiring

**Deliverables:**

- `schnabel/events.py` with the API per [`design.md`](design.md).
- `memory` and `sparql-http` backends.
- bfg's `local_commit` (smallest method, no network) wired to emit invocation/snapshot quads.
- A small test: run `local_commit` against a scratch subvol, query the store back, assert what bfg returned matches what the store recorded.
- `QUADSTORE` env var honored; `NullEventLog` when absent.

**No-goals:** MQTT pubsub, byte counting, multi-machine, ACL, backup.py changes.

**Done when:** bfg can be configured to record a structured per-invocation trace; a SPARQL query retrieves the trace.

## Phase 2 — All bfg commands instrumented; backup.py reads back

**Deliverables:**

- Every public bfg command emits invocation quads (entry, exit, key events).
- Parent snapshot picked at `btrfsgit.py:1093` is emitted as `bfg:parentSnapshot`.
- Byte counting plumbed into `local_send`/`remote_send` (Popen chain replacing `shell=True`, byte count emitted as `bfg:bytesTransferred` periodically — or via `pv -bnf`).
- backup.py mints an outer invocation IRI per `_run_backup`; child bfg invocations record `bfg:invokedBy <outer>`.
- backup.py prints a per-subvol summary line after each `ccs("bfg ...")` by querying the store.

**Done when:** the three asks from the original conversation are met. Detailed per-invocation log via graph-per-invocation; parent snapshot surfaced via emitted `bfg:parentSnapshot`; byte accounting via emitted `bfg:bytesTransferred`.

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
