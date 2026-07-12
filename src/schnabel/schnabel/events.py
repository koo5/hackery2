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
from datetime import datetime, timezone
from typing import Any, Callable, Iterable, Optional, Union

from rdflib import Dataset, Literal, URIRef
from rdflib.namespace import RDF, XSD
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore

from . import vocab

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
        """Emit one quad. Terms must be rdflib URIRef/BNode/Literal.
        ``g=None`` writes into the dataset's default graph — discoverable by
        plain SPARQL triple patterns (no GRAPH wrapper needed). This is the
        brn/pyin "default graph for pointers" idiom.
        """
        if self._is_null:
            return
        quad: Quad = (s, p, o, g)
        if self._buffer is not None:
            self._buffer.append(quad)
        else:
            self._write([quad])

    def emit_many(self, quads: Iterable[Quad]) -> None:
        if self._is_null:
            return
        materialized = list(quads)
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
                if g is None:
                    self._nquads_file.write(f"{s.n3()} {p.n3()} {o.n3()} .\n")
                else:
                    self._nquads_file.write(
                        f"{s.n3()} {p.n3()} {o.n3()} {g.n3()} .\n"
                    )
            self._nquads_file.flush()
        else:
            assert self._dataset is not None
            for s, p, o, g in quads:
                if g is None:
                    self._dataset.add((s, p, o))
                else:
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
        """Atomically replace ``s p ?o`` with ``s p o``.

        The brn / pyin "latest pointer" idiom. Stable subject; ``rdf:value``-style
        predicate; the object is the current pointer-target. ``g=None`` lands in
        the dataset's default graph so consumers can query without a GRAPH wrapper.
        """
        if self._is_null:
            return
        if self._dataset is None:
            raise NotImplementedError(
                "pointer_swap requires a queryable backend (memory or sparql-http)"
            )
        if g is None:
            self._dataset.remove((s, p, None))
            self._dataset.add((s, p, o))
        else:
            graph_handle = self._dataset.graph(g)
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

    # --- high-level: invocation lifecycle ---------------------------------

    @contextlib.contextmanager
    def invocation(self, type_iri: URIRef, *,
                   suffix: Optional[str] = None,
                   parent: Optional[URIRef] = None):
        """Wrap a unit of work as an invocation graph.

        On entry: mint a fresh graph IRI, emit ``(inv rdf:type <type_iri>)``,
        ``startedAt``, and — if a parent invocation was passed or found in the
        ``SCHNABEL_PARENT_INVOCATION`` env var — ``(inv core:invokedBy <parent>)``.
        Swap the ``latest_invocation`` pointer to this invocation.

        On normal exit: emit ``status=complete`` and ``endedAt``.
        On exception: emit ``status=failed``, ``error``, ``endedAt``, re-raise.

        Yields an ``_InvocationHandle`` that gives the body convenient
        graph-scoped ``emit()`` and ``emit_about()``. In null-mode the handle's
        IRI is ``None`` and all its methods are no-ops.

        :param parent: explicit parent invocation IRI. Takes precedence over
            the ``SCHNABEL_PARENT_INVOCATION`` env var when both are present.
        """
        if self._is_null:
            yield _InvocationHandle(self, None)
            return

        if suffix is None:
            # Derive a short suffix from the type IRI's last segment so the
            # graph IRI is a bit more debuggable: urn:schnabel:graph:<uuid>_localcommit
            tail = str(type_iri)
            for sep in (":", "/", "#"):
                if sep in tail:
                    tail = tail.rsplit(sep, 1)[-1]
            suffix = tail.lower()

        inv = self.graph(suffix=suffix)
        started = datetime.now(timezone.utc).isoformat()

        # Parent-invocation linkage: explicit arg > env var > none.
        if parent is None:
            env_parent = os.environ.get("SCHNABEL_PARENT_INVOCATION", "").strip()
            if env_parent:
                parent = URIRef(env_parent)
        elif not isinstance(parent, URIRef):
            parent = URIRef(str(parent))

        with self.batch():
            self.emit(inv, RDF.type, type_iri, g=inv)
            self.emit(inv, vocab.started_at,
                Literal(started, datatype=XSD.dateTime), g=inv)
            if parent is not None:
                self.emit(inv, vocab.invoked_by, parent, g=inv)
            self.pointer_swap(vocab.latest_invocation, vocab.points_to, inv)

        # Propagate this invocation as the ambient parent for any subprocess
        # spawned inside the body. Schnabel's W3C-TRACEPARENT-style cross-process
        # linkage (D-012). Restored in the finally below regardless of how the
        # body exits, including on exception. Single-threaded only — concurrent
        # invocations on the same process would stomp on each other.
        prev_env = os.environ.get("SCHNABEL_PARENT_INVOCATION")
        os.environ["SCHNABEL_PARENT_INVOCATION"] = str(inv)

        handle = _InvocationHandle(self, inv)
        try:
            try:
                yield handle
            except BaseException as exc:
                with self.batch():
                    self.emit(inv, vocab.status, vocab.STATUS_FAILED, g=inv)
                    self.emit(inv, vocab.error, Literal(str(exc)), g=inv)
                    self.emit(inv, vocab.ended_at,
                        Literal(datetime.now(timezone.utc).isoformat(),
                                datatype=XSD.dateTime), g=inv)
                raise

            with self.batch():
                self.emit(inv, vocab.status, vocab.STATUS_COMPLETE, g=inv)
                self.emit(inv, vocab.ended_at,
                    Literal(datetime.now(timezone.utc).isoformat(),
                            datatype=XSD.dateTime), g=inv)
        finally:
            if prev_env is None:
                os.environ.pop("SCHNABEL_PARENT_INVOCATION", None)
            else:
                os.environ["SCHNABEL_PARENT_INVOCATION"] = prev_env

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


class _InvocationHandle:
    """Graph-scoped facade yielded by ``EventLog.invocation()``.

    Carries the invocation IRI and provides ``emit()`` / ``emit_about()`` that
    automatically scope to the invocation's graph. In null-mode ``iri`` is
    ``None`` and all methods short-circuit.
    """

    __slots__ = ("log", "iri")

    def __init__(self, log: "EventLog", iri: Optional[URIRef]):
        self.log = log
        self.iri = iri

    def emit(self, p, o) -> None:
        """Emit ``(iri, p, o)`` in the invocation's graph."""
        if self.iri is None:
            return
        self.log.emit(self.iri, p, o, g=self.iri)

    def emit_about(self, s, p, o) -> None:
        """Emit ``(s, p, o)`` in the invocation's graph — for child resources
        (e.g. a snapshot the invocation produced) where ``s`` isn't the
        invocation itself."""
        if self.iri is None:
            return
        self.log.emit(s, p, o, g=self.iri)

    def bn(self, suffix: str = "") -> URIRef:
        return self.log.bn(suffix=suffix)
