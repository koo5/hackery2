"""Exercise the EventLog API against the memory backend."""

import json
import os

import pytest
from rdflib import Literal, URIRef

from schnabel.events import EventLog, parse_descriptor
from schnabel.vocab import BFG, latest_invocation, points_to


# ---------------------------------------------------------------------------
# Descriptor parsing
# ---------------------------------------------------------------------------


def test_parse_descriptor_inline_json5():
    cfg = parse_descriptor("{ backend: 'memory' }")
    assert cfg == {"backend": "memory"}


def test_parse_descriptor_file_reference(tmp_path):
    p = tmp_path / "q.json5"
    p.write_text('{ backend: "memory", path: "/tmp/x.nq" }')
    cfg = parse_descriptor(f"@{p}")
    assert cfg["backend"] == "memory"
    assert cfg["path"] == "/tmp/x.nq"


def test_parse_descriptor_empty_returns_none():
    assert parse_descriptor(None) is None
    assert parse_descriptor("") is None
    assert parse_descriptor("   ") is None


# ---------------------------------------------------------------------------
# Null mode
# ---------------------------------------------------------------------------


def test_null_mode_when_no_config(monkeypatch):
    monkeypatch.delenv("QUADSTORE", raising=False)
    log = EventLog()
    assert log.is_null is True
    # All operations should be no-ops, not errors.
    log.emit(URIRef("x:a"), URIRef("x:b"), Literal("c"))
    log.emit_many([(URIRef("x:a"), URIRef("x:b"), Literal("c"), None)])
    with log.batch():
        log.emit(URIRef("x:a"), URIRef("x:b"), Literal("c"))
    log.close()


# ---------------------------------------------------------------------------
# Memory backend roundtrip
# ---------------------------------------------------------------------------


def test_emit_and_query_memory():
    log = EventLog({"backend": "memory"})
    inv = log.graph(suffix="invocation")
    log.emit(inv, BFG.onHost, Literal("testhost"), g=inv)
    log.emit(inv, BFG.status, Literal("complete"), g=inv)

    results = list(
        log.query(
            "SELECT ?host WHERE { GRAPH ?g { ?inv <urn:schnabel:vocab:bfg:onHost> ?host } }"
        )
    )
    assert len(results) == 1
    assert str(results[0][0]) == "testhost"
    log.close()


def test_batch_flushes_atomically():
    log = EventLog({"backend": "memory"})
    inv = log.graph(suffix="invocation")
    with log.batch():
        log.emit(inv, BFG.onHost, Literal("h"), g=inv)
        log.emit(inv, BFG.status, Literal("running"), g=inv)
        # During the batch, nothing has been written yet.
        assert list(log.quads(inv)) == []
    # After exit, both quads are present.
    assert len(list(log.quads(inv))) == 2
    log.close()


def test_nested_batch_flushes_only_at_outer_exit():
    log = EventLog({"backend": "memory"})
    inv = log.graph()
    with log.batch():
        log.emit(inv, BFG.onHost, Literal("a"), g=inv)
        with log.batch():
            log.emit(inv, BFG.status, Literal("running"), g=inv)
            assert list(log.quads(inv)) == []
        # Inner exit did not flush.
        assert list(log.quads(inv)) == []
    assert len(list(log.quads(inv))) == 2
    log.close()


def test_pointer_swap_replaces_prior_value():
    log = EventLog({"backend": "memory"})
    a = URIRef("urn:test:a")
    b = URIRef("urn:test:b")
    log.pointer_swap(latest_invocation, points_to, a)
    log.pointer_swap(latest_invocation, points_to, b)

    matches = list(log.query(
        "SELECT ?o WHERE { GRAPH ?g { <urn:schnabel:vocab:core:latest_invocation> "
        "<urn:schnabel:vocab:core:points_to> ?o } }"
    ))
    assert len(matches) == 1
    assert matches[0][0] == b
    log.close()


def test_default_graph_used_when_g_omitted():
    log = EventLog({"backend": "memory", "default_graph": "urn:test:default"})
    log.emit(URIRef("x:a"), BFG.onHost, Literal("h"))
    quads = list(log.quads())
    assert len(quads) == 1
    # rdflib yields the graph term as a URIRef directly.
    assert str(quads[0][3]) == "urn:test:default"
    log.close()


# ---------------------------------------------------------------------------
# nquads-file backend
# ---------------------------------------------------------------------------


def test_nquads_file_appends(tmp_path):
    path = tmp_path / "out.nq"
    log = EventLog({"backend": "nquads-file", "path": str(path)})
    inv = log.graph()
    log.emit(inv, BFG.onHost, Literal("h"), g=inv)
    log.emit(inv, BFG.status, Literal("complete"), g=inv)
    log.close()

    lines = path.read_text().strip().split("\n")
    assert len(lines) == 2
    assert "urn:schnabel:vocab:bfg:onHost" in lines[0]
    assert "complete" in lines[1]


def test_nquads_file_rejects_query(tmp_path):
    log = EventLog({"backend": "nquads-file", "path": str(tmp_path / "out.nq")})
    with pytest.raises(NotImplementedError):
        log.query("SELECT * WHERE { ?s ?p ?o }")
    log.close()


# ---------------------------------------------------------------------------
# Persistence round-trip
# ---------------------------------------------------------------------------


def test_memory_persistence_roundtrip(tmp_path):
    path = tmp_path / "store.nq"
    inv = URIRef("urn:test:inv")

    log1 = EventLog({"backend": "memory", "path": str(path)})
    log1.emit(inv, BFG.onHost, Literal("h"), g=inv)
    log1.close()

    log2 = EventLog({"backend": "memory", "path": str(path)})
    quads = list(log2.quads(inv))
    assert len(quads) == 1
    assert str(quads[0][2]) == "h"
    log2.close()


# ---------------------------------------------------------------------------
# QUADSTORE env var
# ---------------------------------------------------------------------------


def test_config_from_env(monkeypatch):
    monkeypatch.setenv("QUADSTORE", '{ backend: "memory" }')
    log = EventLog()
    assert log.is_null is False
    assert log.config == {"backend": "memory"}
    log.close()
