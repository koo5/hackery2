# Vision

## The walled garden we're tired of

Today's tools talk to each other through a thicket of bespoke channels: stdout text with ad-hoc framing, files in ad-hoc directories, JSON over ad-hoc sockets, env vars passed through ad-hoc plumbing. Every pair of programs negotiates its own protocol, every protocol is its own dialect, and the "audit log" of what happened is whatever each program happens to print.

This works in the sense that planes work: thrust over drag. It does not work in the sense that a coherent computing environment should — where any program can ask "what happened" and "what's true now" without being privileged as the asker.

## The shift

A semantic desktop reframes this by treating cooperating processes as participants in a shared, RDF-shaped runtime state:

1. **Process state is RDF.** Each fact a program asserts during operation is a triple, or — with provenance — a quad.
2. **Cooperating processes share a quadstore.** Local-only at first; cross-machine through well-known boundaries (SPARQL HTTP, MQTT) when needed.
3. **The audit log, the I/O channel, the persistence layer, the inspectability surface, and the extensibility hook are the same thing.** Not because we deduplicated them — because they were never separate to begin with.

Each process is now free to **speak**, in the literal sense: assert facts into a shared space that other processes — and humans, with SPARQL — can read, join, query, replay, and act on. Speech is append-only. The bus carries the speech. The store keeps it.

## What's distinctive

- **The same triples are simultaneously the message, the record, and the API.** A process emits a fact; another process reads it; a year later a human queries the same fact. One representation, three uses.
- **Communication is a first-class concern**, not a side effect of logging. A process subscribing to "all new triples in graph X" is what enables realtime introspection without the producer having to know about it.
- **Append-only by default.** Mutation happens via the pointer idiom (a stable subject whose `rdf:value` is swapped atomically). The store keeps every prior assertion. Garbage collection is a separate, intentional act.

## What we are *not* doing

- Not building a new triplestore. We use the boring ones.
- Not inventing a new wire protocol. SPARQL 1.1 and MQTT do the job.
- Not declaring an upfront ontology. Predicates earn their place by being used.
- Not making JSON the canonical form. RDF is. JSON-LD is a presentation layer for when humans need to read or non-RDF-aware consumers need to consume.

## The trajectory

Phase 1 lets `bfg` and `backup.py` have a structured per-invocation audit trail and live progress. Phase 5 is when most of the tooling on this machine emits its salient state into the same store, and querying "what happened on this host this hour" or "what's currently in flight" is a one-line SPARQL.

The intermediate phases are in [`roadmap.md`](roadmap.md).
