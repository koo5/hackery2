# Prior art

Distilled notes from existing systems we studied, with code excerpts to anchor each lesson. File:line refs let future-you re-find the originals without re-reading the prototypes.

## brn — RDF-as-IPC via a triplestore

**Source:** `~/repos/koo5/brn/0/brn/`. A click-based CLI that passes data between phases through an AllegroGraph triplestore instead of files.

### What to copy

**Pointer indirection.** A small vocab — `rdf:value` + `rdf2:data_is_in_graph` — turns "where is the data" into a single dereferenceable IRI:

```python
# brn/sparql_helper.py:101
def construct_pointer(conn, iri, graph):
    id = bn(conn, 'pointer')
    conn.addData({
        '@context': pointer_namespaces,
        '@id': id,
        'rdf:value': {'@id': iri},
        'rdf2:data_is_in_graph': {'@id': graph}})
    return id
```

The default graph stays small (only pointers); bulk data lives in named graphs.

**Bnodes-as-fresh-IDs.** Per-process unique IRIs minted from the store, used as `@id` for new assertions:

```python
# brn/sparql_helper.py:131
def bn(conn, suffix=''):
    if suffix:
        suffix = '_' + suffix
    return 'https://rdf.localhost/bn/' + conn.createBNode().id[2:] + suffix
```

Avoids manual UUID minting. (For schnabel we use UUID4 → URN directly; no store round-trip needed.)

**Named graphs per task.** Each `parse_tau_testcases` run gets its own graph; the default graph holds only the pointer (`brn/cli.py:122-145`). Clean audit story.

### What to avoid

- Hard binding to AllegroGraph and Franz's Python SDK. Heavy setup, env vars per connection field.
- The AllegroGraph JSON-LD list-reversal bug (acknowledged in `brn/cli.py:130`). Use rdflib + n-quads or proper SPARQL UPDATE instead.
- Phase-based ("write graph, next phase reads graph") with no realtime story.

## pyin — RDF-as-runtime-trace at high rate

**Source:** `~/repos/koo5/univar/0/univar/pyin/`. An N3 reasoner emitting its proof trace as RDF, both to a `.n3` file and to a SPARQL endpoint.

### The architecture, in one diagram

```
reasoner step → kbdbg(text) ──┬──► kbdbg_text(text+'.') ───► .n3 file on disk
                              │
                              └──► to_submit_graph += text+'. '   (accumulator)
                                          │
                                          │  on step() boundary
                                          ▼
                                   all_updates += "INSERT DATA { GRAPH <step_N> { … } };"
                                          │
                                          │  every 100 KB
                                          ▼
                          pool.submit(server.update, …)  (ThreadPoolExecutor)
                                          │
                                          ▼
                                   pymantic.sparql.SPARQLServer
```

### What to copy

**Graph-per-step, threaded into a list.** Each reasoning step gets a fresh graph name; the graphs are wired into an RDF list at the default graph:

```python
# pyin/pyin.py:78-87
def step_graph_name(idx):
    return this + '_' + str(idx).rjust(10, '0')

def step_list_item(idx):
    if idx == 0:
        return this
    return step_graph_name(idx) + "_list_item"

def kbdbg_graph_first():
    kbdbg('<' + step_list_item(global_step_counter) + "> rdf:first <" +
          step_graph_name(global_step_counter) + '>', True)
```

The temporal sequence of work *is* an RDF structure — no out-of-band "log file timestamp" needed. Schnabel does this at the invocation level, not per step.

**The "latest" pointer.** `DELETE … INSERT …` swap publishes the current run:

```python
# pyin/pyin_main.py:42-48
new = """kbdbg:latest kbdbg:is <""" + this + ">"
pyin.kbdbg(new, default=True)
uuu = (pyin.prefixes +
    """DELETE {kbdbg:latest kbdbg:is ?x} WHERE {kbdbg:latest kbdbg:is ?x}""")
server.update(uuu)
```

Same idiom as brn's `localhost:last_tau_testcases_parsed`. Appearing in two prototypes ⇒ a primitive we should keep.

**Two sinks, one source.** The *same* `kbdbg(text)` call writes both to a `.n3` file *and* into the SPARQL accumulator (`pyin/pyin.py:35-45`). Both sinks materialize the same triples; neither is privileged. The disk file is just one materialization of the stream — exactly the architecture we want.

**Async submit with backpressure** (`pyin/pyin.py:53-58`):

```python
qs = pool._work_queue.qsize()
while qs > 100:
    print("sleeping " + str(qs - 100))
    sleep(qs - 100)
    qs = pool._work_queue.qsize()
```

Crude but effective.

### What to avoid

**String-concatenated SPARQL UPDATE bodies** (`pyin/pyin.py:61`):

```python
all_updates += "INSERT DATA {Graph <" + step_graph_name(...) + "> {" + to_submit_graph + '}};'
```

Each `kbdbg(text)` is itself built by string-concatenating n3 fragments. The server has to re-parse all of it. Going through rdflib's typed terms + `SPARQLUpdateStore.addN(quads)` emits a properly-formed UPDATE without the string-shuffling tax.

**Per-tiny-event emission with ~5-7 triples per logical event.** `emit_binding` is 3 triples, `emit_arg` 4-7, `emit_term` 3, each step calls these multiple times. For a deep proof, most CPU is spent emitting trace triples. The lesson: **batch what's logically one event** via a `with log.batch():` primitive — pyin doesn't have one; its accumulator + size-threshold is a workaround.

**The `nolog` global as kill-switch.** Hundreds of `if not nolog:` guards (`pyin/pyin.py:194, 218, 325, 339, …`). Symptom of an emit API that wasn't cheap enough when disabled. Cleaner: `NullEventLog` is the no-op polymorphic alternative; call sites stay unconditional.

**Flush threshold tied to byte length** (`> 100000` chars in the accumulator). Tying batch boundaries to text generated rather than logical units couples emit cadence to vocab verbosity. We want logical boundaries.

**No transactionality / no rollback.** `pool.submit(...)` returns a future; by the time the future fails, more updates are already in flight. Graph-per-invocation lets us do better: a closing triple `(<inv> bfg:status "complete")` becomes the atomic "this graph is now durable" marker; queries can filter to it to exclude in-flight or crashed invocations.

**No subscriber path.** The `.n3` file is post-hoc (`kbdbg2graphviz.py` reads it later); the SPARQL store *could* be queried live, but nothing pushes. Pyin had no realtime view of itself running. That's exactly the gap schnabel closes.

## app.js — JSON-LD as a presentation layer

**Source:** `~/repos/lodgeit-labs/accounts-assessor/0/accounts-assessor/sources/js-services/src/app.js`. A small Express service that frames RDF into compact JSON-LD for non-RDF consumers.

### What to copy

**Frame + simplify + clean** as a pure presentation pipeline:

```js
// app.js:147 — unwrap rdf:value wrappers
async function simplify(frame) {
    let f = await cars_framed(source);
    let items = f['@graph'][0]['rdf:value']['@list'];
    items.forEach(i => {
        for (const [key, value] of Object.entries(i)) {
            let v = value['rdf:value'];
            if (v !== undefined)
                i[key] = v;
        }
    });
    return items;
}

// app.js:177 — delete decorative predicates
function clean(data) { /* recursively drops excel:row, excel:col, ... */ }
```

For `bfg events <inv>` or a `bfg-watch` TUI we'll do something analogous: frame the invocation graph, simplify nested `rdf:value`s, drop low-value predicates. Wire format stays triples; presentation is JSON-LD after a frame.

### What to avoid

**`do_add_type2_quads`** (`app.js:118-142`) is a workaround for a JSON-LD library bug where `@reverse rdf:type` doesn't work. Don't synthesize duplicate quads in the consumer; do reverse reasoning in a SPARQL `CONSTRUCT` upstream.

## AllegroGraph — proprietary but their ACL is good

Per-statement ACL with role-based filtering. Triggers and SSE for change notifications. Battle-tested.

**Why not use it:** proprietary, license-encumbered, and the user has explicitly moved away. The lesson to absorb: granular ACL on the SPARQL side is achievable. Schnabel's ACL lives one layer up (per-dataset via Fuseki+Shiro, plus topic-level on MQTT).

## Tracker3 — installed everywhere, but the graph-policy is a deal-breaker

GNOME's local SPARQL endpoint, DBus signals on update, on most modern Linux distros by default.

**Why not for v1 (D-005):**

- Every graph IRI written to must be **pre-registered** in the connection's graph policy. Our `urn:schnabel:graph:<uuid>_invocation` pattern fights this.
- Notifications via DBus carry **deltas as resource IRIs**, not full triples — subscriber must SPARQL-query back. Fine for low rate, amplifies for high.
- DBus signals are local-only; cross-machine pubsub still needs a relay.
- Ontology must be declared upfront in a `.ontology` file (we picked code-first; see D-002).

**What it does well that we should match:** per-graph ACL primitive. Federation between local Tracker instances. The HTTP endpoint shim is a model for "expose this store to a peer."

## Apache Jena Fuseki — boring, mature, our likely v1+ backend

Mature SPARQL 1.1 store with persistent TDB2 backend. Authentication via Shiro: roles, per-dataset access. Battle-tested in enterprise deployments. Active OSS community. "Tracker but without the ontology straightjacket."

**Use it for:** the SPARQL endpoint in any deployment where we want auth on the store.

## Oxigraph — single-binary aesthetics, no auth

SPARQL 1.1 server in a single Rust binary. RocksDB-backed, ~50 MB binary, no daemon you didn't write. No auth out of the box; needs a reverse proxy.

**Use it for:** local-machine dev convenience, single-user deploys. Sidecar approach (oxigraph + nginx-with-basic-auth) covers single-machine multi-process when Fuseki feels like overkill.

## MQTT — the boring pubsub

Eclipse Mosquitto, EMQX, HiveMQ. Username/password and TLS client cert auth. Topic-level ACLs. Retained messages, QoS levels, last-will-and-testament. v5 supports per-message `Content-Type` (we'll set `application/n-quads`).

**Use it for:** schnabel's pubsub layer (D-004). Each emit publishes to a topic derived from the graph IRI; subscribers filter by topic prefix. Payload is the actual quad batch in n-quads — not a "go check the store" notification — for a single round-trip in the common case.

## Connection-descriptor surface — postgres URL vs JSON5

PostgreSQL connection strings (`postgresql://user:pass@host:port/dbname?ssl=true`) are the familiar template for "URL-shaped descriptor." Workable for flat fields; painful when:

- Nested structures (pubsub sub-config, multiple endpoints).
- Auth options beyond user/pass (token, OAuth, mTLS).
- Future extensions where unknown keys must roundtrip.

JSON5 (with `@/path/to/file` escape hatch) handles all of the above; the human-friendliness gap is small. See D-001.
