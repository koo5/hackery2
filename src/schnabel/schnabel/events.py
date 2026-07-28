"""EventLog: backend-agnostic, RDF-shaped, append-only runtime-state recorder.

See ../docs/design.md for the API contract and ../docs/decisions.md (D-001..D-008)
for the choices behind it. This module deliberately stays minimal in phase 1:
``memory``, ``nquads-file``, and ``sparql-http`` backends; ``subscribe()`` is a
stub until phase 3 (MQTT).
"""

from __future__ import annotations

import contextlib
import os
import uuid
from typing import Any, Callable, Iterable, Optional, Union

from rdflib import Dataset, Literal, URIRef
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore

try:
    import json5 as _jsonlib
except ImportError:  # pragma: no cover - fallback for environments without json5
    import json as _jsonlib


DEFAULT_GRAPH = URIRef("urn:schnabel:default")


# ---------------------------------------------------------------------------
# Descriptor parsing
# ---------------------------------------------------------------------------


def _expand(path: str) -> str:
    return os.path.expanduser(os.path.expandvars(path))


def parse_descriptor(raw: Optional[str]) -> Optional[dict]:
    """Parse a QUADSTORE-shaped string.

    Accepts inline JSON5 or ``@/path/to/file``. Returns ``None`` when input is
    absent or empty so callers can treat that as "no log configured".
    """
    if raw is None:
        return None
    raw = raw.strip()
    if not raw:
        return None
    if raw.startswith("@"):
        with open(_expand(raw[1:]), "r", encoding="utf-8") as f:
            return _jsonlib.loads(f.read())
    return _jsonlib.loads(raw)


# ---------------------------------------------------------------------------
# EventLog
# ---------------------------------------------------------------------------


Quad = tuple  # (s, p, o, g)


class EventLog:
    """Structured event log over a quadstore. See ../docs/design.md.

    Resolution order for config: explicit argument > ``QUADSTORE`` env var >
    no-op mode. In no-op mode every method is a fast return; call sites stay
    unconditional (D-002 lesson from pyin's ``nolog`` global).
    """

    # --- construction -----------------------------------------------------

    def __init__(self, config: Optional[Union[dict, str]] = None):
        if config is None:
            config = parse_descriptor(os.environ.get("QUADSTORE"))
        elif isinstance(config, str):
            config = parse_descriptor(config)

        self.config: Optional[dict] = config
        self._buffer: Optional[list[Quad]] = None
        self._closed = False
        self._dataset: Optional[Dataset] = None
        self._nquads_file = None
        self._persist_path: Optional[str] = None

        if config is None:
            self._is_null = True
            return

        self._is_null = False
        self._default_graph = URIRef(config.get("default_graph", DEFAULT_GRAPH))
        backend = config.get("backend", "memory")
        self._backend = backend

        if backend == "memory":
            self._dataset = Dataset()
            persist = config.get("path")
            if persist:
                self._persist_path = _expand(persist)
                if os.path.exists(self._persist_path):
                    self._dataset.parse(self._persist_path, format="nquads")
        elif backend == "nquads-file":
            path = _expand(config["path"])
            parent = os.path.dirname(path)
            if parent:
                os.makedirs(parent, exist_ok=True)
            self._nquads_file = open(path, "a", encoding="utf-8")
        elif backend == "sparql-http":
            endpoint = config["endpoint"]
            store = SPARQLUpdateStore(
                query_endpoint=endpoint,
                update_endpoint=config.get("update_endpoint", endpoint),
            )
            auth = config.get("auth") or {}
            if auth.get("kind") == "basic":
                store.setCredentials(auth["user"], auth["password"])
            # Note: SPARQLUpdateStore opens lazily on first use.
            self._dataset = Dataset(store=store)
        else:
            raise ValueError(f"unknown backend: {backend!r}")

    # --- emit -------------------------------------------------------------

    def emit(self, s, p, o, g=None) -> None:
        """Emit one quad. Terms must be rdflib URIRef/BNode/Literal."""
        if self._is_null:
            return
        quad: Quad = (s, p, o, g if g is not None else self._default_graph)
        if self._buffer is not None:
            self._buffer.append(quad)
        else:
            self._write([quad])

    def emit_many(self, quads: Iterable[Quad]) -> None:
        if self._is_null:
            return
        materialized = [
            (s, p, o, g if g is not None else self._default_graph)
            for (s, p, o, g) in quads
        ]
        if self._buffer is not None:
            self._buffer.extend(materialized)
        else:
            self._write(materialized)

    @contextlib.contextmanager
    def batch(self):
        """Buffer emits inside the block; flush atomically on exit.

        Nested batches flatten into the outermost one (the inner ``__exit__``
        does not flush; only the outermost one does).
        """
        if self._is_null:
            yield
            return
        if self._buffer is not None:
            yield
            return
        self._buffer = []
        try:
            yield
        finally:
            buf, self._buffer = self._buffer, None
            if buf:
                self._write(buf)

    def _write(self, quads: list[Quad]) -> None:
        if self._backend == "nquads-file":
            assert self._nquads_file is not None
            for s, p, o, g in quads:
                self._nquads_file.write(
                    f"{s.n3()} {p.n3()} {o.n3()} {g.n3()} .\n"
                )
            self._nquads_file.flush()
        else:
            assert self._dataset is not None
            for s, p, o, g in quads:
                self._dataset.add((s, p, o, g))

    # --- identifiers ------------------------------------------------------

    @staticmethod
    def bn(suffix: str = "") -> URIRef:
        """Mint ``urn:schnabel:bn:<uuid4>[_suffix]``. No store round-trip."""
        ident = uuid.uuid4().hex
        if suffix:
            return URIRef(f"urn:schnabel:bn:{ident}_{suffix}")
        return URIRef(f"urn:schnabel:bn:{ident}")

    @staticmethod
    def graph(suffix: str = "") -> URIRef:
        """Mint ``urn:schnabel:graph:<uuid4>[_suffix]``."""
        ident = uuid.uuid4().hex
        if suffix:
            return URIRef(f"urn:schnabel:graph:{ident}_{suffix}")
        return URIRef(f"urn:schnabel:graph:{ident}")

    # --- pointer idiom ----------------------------------------------------

    def pointer_swap(self, s, p, o, g=None) -> None:
        """Atomically replace ``s p ?o`` with ``s p o`` in ``g``.

        The brn / pyin "latest pointer" idiom. Stable subject; ``rdf:value``-style
        predicate; the object is the current pointer-target.
        """
        if self._is_null:
            return
        if self._dataset is None:
            raise NotImplementedError(
                "pointer_swap requires a queryable backend (memory or sparql-http)"
            )
        target = g if g is not None else self._default_graph
        graph_handle = self._dataset.graph(target)
        graph_handle.remove((s, p, None))
        graph_handle.add((s, p, o))

    # --- query ------------------------------------------------------------

    def query(self, sparql: str):
        if self._is_null:
            return []
        if self._dataset is None:
            raise NotImplementedError(
                "query requires a queryable backend (memory or sparql-http)"
            )
        return self._dataset.query(sparql)

    def quads(self, graph: Optional[URIRef] = None) -> Iterable[Quad]:
        """Iterate quads, optionally filtered to one graph. Convenience for
        callers that want the raw store contents without writing SPARQL."""
        if self._is_null or self._dataset is None:
            return iter(())
        if graph is None:
            return self._dataset.quads()
        return self._dataset.quads((None, None, None, graph))

    # --- subscribe (phase 3) ----------------------------------------------

    def subscribe(self, graph_pattern, callback: Callable[[list[Quad]], None]) -> None:
        raise NotImplementedError("subscribe lands in phase 3 (MQTT backend)")

    # --- lifecycle --------------------------------------------------------

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._is_null:
            return
        if self._backend == "memory" and self._persist_path:
            data = self._dataset.serialize(format="nquads")
            parent = os.path.dirname(self._persist_path)
            if parent:
                os.makedirs(parent, exist_ok=True)
            with open(self._persist_path, "w", encoding="utf-8") as f:
                f.write(data)
        elif self._backend == "nquads-file" and self._nquads_file is not None:
            self._nquads_file.close()

    def __enter__(self) -> "EventLog":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    # --- introspection ----------------------------------------------------

    @property
    def is_null(self) -> bool:
        """True when no config was provided/found and all operations are no-ops."""
        return self._is_null
