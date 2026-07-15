"""Exercise the EventLog API against the memory backend."""

import json
import os

import pytest
from rdflib import Literal, URIRef
from rdflib.namespace import RDF

from schnabel.events import EventLog, parse_descriptor
from schnabel.vocab import (
    BFG,
    latest_invocation,
    points_to,
    started_at,
    ended_at,
    status as status_pred,
    error as error_pred,
    invoked_by,
    STATUS_COMPLETE,
    STATUS_FAILED,
)


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

    # Pointer lives in the default graph; query without a GRAPH wrapper.
    matches = list(log.query(
        "SELECT ?o WHERE { <urn:schnabel:vocab:core:latest_invocation> "
        "<urn:schnabel:vocab:core:points_to> ?o }"
    ))
    assert len(matches) == 1
    assert matches[0][0] == b
    log.close()


def test_emit_without_g_lands_in_default_graph_queryable_plainly():
    """When emit() is called without g, the quad goes into rdflib's default
    graph — queryable by SPARQL without a GRAPH wrapper. This is the brn/pyin
    'pointer in the default graph' idiom."""
    log = EventLog({"backend": "memory"})
    log.emit(URIRef("x:a"), BFG.onHost, Literal("h"))
    rows = list(log.query(
        "SELECT ?o WHERE { <x:a> <urn:schnabel:vocab:bfg:onHost> ?o }"
    ))
    assert len(rows) == 1
    assert str(rows[0][0]) == "h"
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


# ---------------------------------------------------------------------------
# invocation() context manager
# ---------------------------------------------------------------------------


def test_invocation_happy_path_emits_lifecycle_quads():
    log = EventLog({"backend": "memory"})
    with log.invocation(BFG.LocalCommit) as inv:
        inv.emit(BFG.onHost, Literal("h"))
    assert inv.iri is not None

    quads = list(log.quads(inv.iri))
    preds = {str(q[1]) for q in quads}
    assert str(RDF.type) in preds
    assert str(started_at) in preds
    assert str(ended_at) in preds
    assert str(status_pred) in preds
    assert str(BFG.onHost) in preds

    status_rows = list(log.query(
        f"SELECT ?s WHERE {{ GRAPH <{inv.iri}> {{ <{inv.iri}> <{status_pred}> ?s }} }}"
    ))
    assert {str(r[0]) for r in status_rows} == {str(STATUS_COMPLETE)}

    # latest_invocation pointer was swapped to this invocation.
    ptr_rows = list(log.query(
        f"SELECT ?i WHERE {{ <{latest_invocation}> <{points_to}> ?i }}"
    ))
    assert [str(r[0]) for r in ptr_rows] == [str(inv.iri)]
    log.close()


def test_invocation_failure_path_emits_failed_status_and_error():
    log = EventLog({"backend": "memory"})

    with pytest.raises(RuntimeError, match="boom"):
        with log.invocation(BFG.LocalCommit) as inv:
            inv.emit(BFG.onHost, Literal("h"))
            raise RuntimeError("boom")

    status_rows = list(log.query(
        f"SELECT ?s WHERE {{ GRAPH <{inv.iri}> {{ <{inv.iri}> <{status_pred}> ?s }} }}"
    ))
    assert {str(r[0]) for r in status_rows} == {str(STATUS_FAILED)}

    err_rows = list(log.query(
        f"SELECT ?e WHERE {{ GRAPH <{inv.iri}> {{ <{inv.iri}> <{error_pred}> ?e }} }}"
    ))
    assert any("boom" in str(r[0]) for r in err_rows)
    log.close()


def test_invocation_null_mode_yields_no_op_handle(monkeypatch):
    monkeypatch.delenv("QUADSTORE", raising=False)
    log = EventLog()
    assert log.is_null is True

    with log.invocation(BFG.LocalCommit) as inv:
        assert inv.iri is None
        # All handle methods must be safe in null-mode.
        inv.emit(BFG.onHost, Literal("h"))
        inv.emit_about(URIRef("x:y"), BFG.abspath, Literal("z"))
        assert inv.bn("snapshot").startswith("urn:schnabel:bn:")
    log.close()


def test_invocation_handle_emit_about_scopes_to_invocation_graph():
    log = EventLog({"backend": "memory"})
    with log.invocation(BFG.LocalCommit) as inv:
        snap = inv.bn("snapshot")
        inv.emit(BFG.snapshot, snap)
        inv.emit_about(snap, BFG.abspath, Literal("/path/to/snap"))

    # The snapshot bnode's abspath should live in the invocation's graph.
    rows = list(log.query(
        f"SELECT ?p WHERE {{ GRAPH <{inv.iri}> {{ <{snap}> <{BFG.abspath}> ?p }} }}"
    ))
    assert [str(r[0]) for r in rows] == ["/path/to/snap"]
    log.close()


def test_invocation_iri_has_lowercase_suffix_derived_from_type():
    log = EventLog({"backend": "memory"})
    with log.invocation(BFG.LocalCommit) as inv:
        pass
    assert str(inv.iri).endswith("_localcommit")
    log.close()


def test_invocation_picks_up_parent_from_env_var(monkeypatch):
    monkeypatch.setenv("SCHNABEL_PARENT_INVOCATION", "urn:schnabel:graph:outer123_runbackup")
    log = EventLog({"backend": "memory"})
    with log.invocation(BFG.LocalCommit) as inv:
        pass

    rows = list(log.query(
        f"SELECT ?p WHERE {{ GRAPH <{inv.iri}> {{ <{inv.iri}> <{invoked_by}> ?p }} }}"
    ))
    assert [str(r[0]) for r in rows] == ["urn:schnabel:graph:outer123_runbackup"]
    log.close()


def test_invocation_no_invoked_by_emit_when_env_var_missing(monkeypatch):
    monkeypatch.delenv("SCHNABEL_PARENT_INVOCATION", raising=False)
    log = EventLog({"backend": "memory"})
    with log.invocation(BFG.LocalCommit) as inv:
        pass

    rows = list(log.query(
        f"SELECT ?p WHERE {{ GRAPH <{inv.iri}> {{ <{inv.iri}> <{invoked_by}> ?p }} }}"
    ))
    assert rows == []
    log.close()


def test_invocation_explicit_parent_overrides_env_var(monkeypatch):
    monkeypatch.setenv("SCHNABEL_PARENT_INVOCATION", "urn:test:env-parent")
    log = EventLog({"backend": "memory"})
    explicit = URIRef("urn:test:explicit-parent")
    with log.invocation(BFG.LocalCommit, parent=explicit) as inv:
        pass

    rows = list(log.query(
        f"SELECT ?p WHERE {{ GRAPH <{inv.iri}> {{ <{inv.iri}> <{invoked_by}> ?p }} }}"
    ))
    assert [str(r[0]) for r in rows] == ["urn:test:explicit-parent"]
    log.close()


def test_invocation_sets_env_var_for_children_while_inside_body(monkeypatch):
    monkeypatch.delenv("SCHNABEL_PARENT_INVOCATION", raising=False)
    log = EventLog({"backend": "memory"})

    seen = {}
    with log.invocation(BFG.LocalCommit) as inv:
        seen["during"] = os.environ.get("SCHNABEL_PARENT_INVOCATION")

    assert seen["during"] == str(inv.iri)
    assert os.environ.get("SCHNABEL_PARENT_INVOCATION") is None
    log.close()


def test_invocation_restores_prior_env_var(monkeypatch):
    monkeypatch.setenv("SCHNABEL_PARENT_INVOCATION", "urn:test:outer")
    log = EventLog({"backend": "memory"})

    with log.invocation(BFG.LocalCommit) as inv:
        # Inside, env var is the new invocation's IRI.
        assert os.environ["SCHNABEL_PARENT_INVOCATION"] == str(inv.iri)

    # On exit, the prior value (which became this invocation's parent) is restored.
    assert os.environ["SCHNABEL_PARENT_INVOCATION"] == "urn:test:outer"
    log.close()


def test_invocation_restores_env_var_on_exception(monkeypatch):
    monkeypatch.setenv("SCHNABEL_PARENT_INVOCATION", "urn:test:outer")
    log = EventLog({"backend": "memory"})

    with pytest.raises(RuntimeError):
        with log.invocation(BFG.LocalCommit):
            raise RuntimeError("boom")

    assert os.environ["SCHNABEL_PARENT_INVOCATION"] == "urn:test:outer"
    log.close()


def test_nested_invocations_form_a_call_tree(monkeypatch):
    """The whole point of the auto-propagation: nested ``with log.invocation()``
    calls build a parent→child→grandchild chain in the store automatically."""
    monkeypatch.delenv("SCHNABEL_PARENT_INVOCATION", raising=False)
    log = EventLog({"backend": "memory"})

    with log.invocation(BFG.LocalCommit) as outer:
        with log.invocation(BFG.Push) as inner:
            with log.invocation(BFG.RemoteCommit) as deepest:
                pass

    # Each inner invocation should record its immediate enclosing invocation.
    def parent_of(child_iri):
        rows = list(log.query(
            f"SELECT ?p WHERE {{ GRAPH <{child_iri}> {{ <{child_iri}> <{invoked_by}> ?p }} }}"
        ))
        return str(rows[0][0]) if rows else None

    assert parent_of(outer.iri) is None  # top level had no env
    assert parent_of(inner.iri) == str(outer.iri)
    assert parent_of(deepest.iri) == str(inner.iri)
    log.close()


def test_invocation_empty_env_var_is_treated_as_absent(monkeypatch):
    monkeypatch.setenv("SCHNABEL_PARENT_INVOCATION", "   ")
    log = EventLog({"backend": "memory"})
    with log.invocation(BFG.LocalCommit) as inv:
        pass
    rows = list(log.query(
        f"SELECT ?p WHERE {{ GRAPH <{inv.iri}> {{ <{inv.iri}> <{invoked_by}> ?p }} }}"
    ))
    assert rows == []
    log.close()
