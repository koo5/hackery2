# Current design

Snapshot of the proposed shape of schnabel. Subject to refactor freely; historical states live in `decisions.md`.

## The API surface (in-process)

```python
class EventLog:
    """Backend-agnostic. Constructor parses JSON5 descriptor from
    QUADSTORE env var or explicit `config` arg."""

    def __init__(self, config: dict | None = None): ...

    # --- emit side ---
    def emit(self, s, p, o, g=None):
        """One quad. Terms are rdflib URIRef / BNode / Literal."""

    def emit_many(self, quads):
        """Iterable of (s, p, o, g) tuples."""

    def batch(self):
        """Context manager. Buffers emits; flushes atomically on __exit__.
        Use this for what's logically one event but takes multiple triples."""

    # --- identifiers ---
    def bn(self, suffix='') -> URIRef:
        """Mint urn:schnabel:bn:<uuid>[_suffix]."""

    def graph(self, suffix='') -> URIRef:
        """Mint urn:schnabel:graph:<uuid>[_suffix]."""

    # --- pointer idiom ---
    def pointer_swap(self, s, p, o, g=None):
        """Atomic DELETE { s p ?o } INSERT { s p o }. From brn / pyin."""

    # --- query / subscribe ---
    def query(self, sparql: str):
        """One-shot SELECT / CONSTRUCT against the store."""

    def subscribe(self, graph_pattern, callback):
        """Realtime: callback(quads) on new quads matching pattern.
        Backed by MQTT if configured, else polled."""

    # --- lifecycle ---
    def close(self): ...
```

Plus `NullEventLog`, whose every method is a no-op, returned when no descriptor is configured. Call sites stay unconditional — no `if log:` guards.

## QUADSTORE descriptor (JSON5)

Single env var `QUADSTORE` carries a JSON5 object. Equivalent forms:

```json5
// inline
QUADSTORE='{
    backend: "sparql-http",
    endpoint: "http://localhost:3030/schnabel",
    auth: { kind: "basic", user: "alice", password: "..." },
    default_graph: "urn:schnabel:default",
    pubsub: {
        kind: "mqtt",
        broker: "tcp://localhost:1883",
        topic_root: "schnabel/",
        auth: { kind: "basic", user: "alice", password: "..." },
    },
}'

// or by file reference
QUADSTORE='@~/.config/schnabel/quadstore.json5'
```

### Known top-level keys (extensible; unknown keys roundtrip)

| Key | Required? | Description |
|---|---|---|
| `backend` | yes | One of: `memory`, `nquads-file`, `sparql-http`. |
| `path` | conditional | For `nquads-file`: where to append. For `memory`: optional persistence path. |
| `endpoint` | for `sparql-http` | Base URL of the SPARQL 1.1 endpoint. |
| `auth` | optional | Auth descriptor. `kind`: `basic`, `bearer`, `mtls`, … |
| `default_graph` | optional | IRI used when an emit doesn't specify `g`. |
| `pubsub` | optional | Sub-descriptor for the notification channel. |

### `pubsub` sub-keys

| Key | Required? | Description |
|---|---|---|
| `kind` | yes | `mqtt`, `polling`. |
| `broker` | for `mqtt` | URL. |
| `topic_root` | optional | Topic-prefix for derived per-graph topics. |
| `qos` | optional | Default QoS. |
| `auth` | optional | Broker creds, separate from store creds. |

## Backends (phase 1 scope)

- **`memory`** — rdflib `Dataset()` in-process; optional `path` to persist on close (n-quads). Zero infrastructure. For tests and very-light usage.
- **`nquads-file`** — append-only n-quads file. No SPARQL queries directly (equivalent to loading into memory at query time).
- **`sparql-http`** — rdflib `SPARQLUpdateStore` against any SPARQL 1.1 endpoint. The real backend.

## Invocation lifecycle

```python
log = EventLog()
inv = log.graph(suffix='invocation')   # urn:schnabel:graph:<uuid>_invocation

with log.batch():
    log.emit(inv, RDF.type, BFG.LocalCommit, g=inv)
    log.emit(inv, BFG.onHost, Literal(hostname), g=inv)
    log.emit(inv, BFG.startedAt, Literal(now, datatype=XSD.dateTime), g=inv)
    log.pointer_swap(BFG.latest_invocation, BFG.points_to, inv)

# ... work happens, emit more events into `inv` graph ...

with log.batch():
    log.emit(inv, BFG.status, Literal("complete"), g=inv)
    log.emit(inv, BFG.endedAt, Literal(now, datatype=XSD.dateTime), g=inv)
```

`bfg:status "complete"` is the atomic "this graph is now durable" marker; queries filter on it to exclude in-flight or crashed invocations.

## Multi-machine sketch (phase 4)

```
   Invoker (host)                                 Invokee (VM)
   ┌──────────────────────────────┐             ┌──────────────────────────────┐
   │ backup.py                    │             │ bfg                          │
   │   │   read-only client       │             │   │   read/write client      │
   │   ▼                          │             │   ▼                          │
   │ (its own SPARQL store        │             │ Fuseki + Shiro              │
   │   for invoker-side events)   │             │   credentials, per-graph ACL│
   │                              │             │                              │
   │ MQTT subscriber ◄────────────┼─── broker ──┼──► MQTT publisher           │
   │ topic: schnabel/inv/+/...    │  (mosquitto)│   topic: schnabel/inv/<uuid>/
   └──────────────────────────────┘             └──────────────────────────────┘
                  │                                            │
                  └──── HTTP GET /sparql?... ──────────────────┘
                         (basic auth or token, read-only)
```

ACL is layered: SSH-tunneled transport, MQTT topic-level ACL (per-publisher and per-subscriber), SPARQL endpoint auth via Shiro. All battle-tested.

## Vocabulary plan

Predicates earn their place by being used (D-002). Initial seed for bfg invocations, expected to evolve:

- `bfg:LocalCommit`, `bfg:RemoteCommit`, `bfg:Push`, `bfg:Pull` (rdf:type values)
- `bfg:onHost` (Literal hostname)
- `bfg:subvol` (Literal abspath)
- `bfg:snapshot` → IRI of a snapshot resource
- `bfg:parentSnapshot` → IRI of the parent snapshot used by `btrfs send`
- `bfg:bytesTransferred` (xsd:long)
- `bfg:startedAt`, `bfg:endedAt` (xsd:dateTime)
- `bfg:status` (Literal: `running`, `complete`, `failed`)
- `bfg:latest_invocation` (default-graph subject, atomic-swap pointer)

The `bfg:` namespace lives at `urn:schnabel:vocab:bfg:` initially; promoted to a stable IRI once the design settles.

## What payload goes on MQTT

Default: **deltas with payload**, not pure "go look" notifications. Each message body is the new quads in n-quads, header `Content-Type: application/n-quads`. ~200–2000 bytes typical for bfg events. Subscriber acts immediately on the payload; SPARQL endpoint stays the durable consistent view for "give me the full invocation graph" / joins.

For high-rate emitters (the pyin failure mode) we may add a "pure indicator" mode later — message body empty, subscriber SPARQL-queries back. Not in phase 1.
