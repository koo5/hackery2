"""Wiring tests for ``backup._run_backup`` + ``backup._print_backup_summary``.

Mocks out ``_do_run_backup`` so we don't need root / btrfs / ssh / Postgres.
Verifies that the outer schnabel invocation is minted, the env var is
propagated and restored, and the summary printer reads the right facts back
from the store.
"""

import importlib
import os
import sys

import pytest

# Import lazily after monkeypatching QUADSTORE so the module-level EventLog
# instance is created with the test configuration.


def _fresh_backup_module(monkeypatch, quadstore_config='{"backend": "memory"}'):
    monkeypatch.setenv("QUADSTORE", quadstore_config)
    if "hackery2.lib.backup" in sys.modules:
        return importlib.reload(sys.modules["hackery2.lib.backup"])
    import hackery2.lib.backup as bu
    return bu


def test_run_backup_mints_outer_and_propagates_env_var(monkeypatch):
    bu = _fresh_backup_module(monkeypatch)

    seen_env = {}

    def fake_do_run_backup(*args, **kwargs):
        seen_env["during"] = os.environ.get("SCHNABEL_PARENT_INVOCATION")

    monkeypatch.setattr(bu, "_do_run_backup", fake_do_run_backup)

    pre = os.environ.get("SCHNABEL_PARENT_INVOCATION")
    bu._run_backup()
    post = os.environ.get("SCHNABEL_PARENT_INVOCATION")

    assert seen_env["during"] is not None
    assert seen_env["during"].startswith("urn:schnabel:graph:")
    assert seen_env["during"].endswith("_runbackup")
    assert post == pre, "env var should be restored after _run_backup exits"


def test_run_backup_restores_env_on_failure(monkeypatch):
    bu = _fresh_backup_module(monkeypatch)

    monkeypatch.setattr(bu, "_do_run_backup", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    monkeypatch.setenv("SCHNABEL_PARENT_INVOCATION", "urn:test:original")

    with pytest.raises(RuntimeError, match="boom"):
        bu._run_backup()

    # Original env var preserved.
    assert os.environ.get("SCHNABEL_PARENT_INVOCATION") == "urn:test:original"


def test_run_backup_emits_outer_invocation_quads(monkeypatch):
    bu = _fresh_backup_module(monkeypatch)
    monkeypatch.setattr(bu, "_do_run_backup", lambda *a, **k: None)

    bu._run_backup(source="testsource", target_machine="testmachine",
                   target_fs="/testfs", local=True, snapshot_only=False)

    rows = list(bu._log.query(f"""
        PREFIX core: <urn:schnabel:vocab:core:>
        SELECT ?inv ?status WHERE {{
            GRAPH ?inv {{
                ?inv a <{bu.BACKUP.RunBackup}> ;
                     core:status ?status .
            }}
        }}
    """))
    assert len(rows) == 1
    inv = rows[0][0]
    assert str(rows[0][1]) == str(bu.schnabel_vocab.STATUS_COMPLETE)

    # Outer carries the parameter facts.
    facts = {(str(p), str(o)) for s, p, o, g in bu._log.quads(inv)}
    assert (str(bu.BACKUP.source), "testsource") in facts
    assert (str(bu.BACKUP.targetMachine), "testmachine") in facts
    assert (str(bu.BACKUP.targetFs), "/testfs") in facts


def test_print_backup_summary_renders_children(monkeypatch, capsys):
    bu = _fresh_backup_module(monkeypatch)
    from rdflib.namespace import XSD

    # Mint outer invocation as backup.py would.
    with bu._log.invocation(bu.BACKUP.RunBackup) as outer:
        # Spawn child invocations that link back via explicit parent= (the
        # env-var path is tested separately by schnabel's own suite).
        with bu._log.invocation(bu.BFG.LocalCommit, parent=outer.iri) as c1:
            c1.emit(bu.BFG.subvol, bu.Literal("/d2/dev3"))
            snap = c1.bn("snapshot")
            c1.emit(bu.BFG.snapshot, snap)
            c1.emit_about(snap, bu.BFG.abspath, bu.Literal("/d2/.bfg_snapshots/dev3_2026-05-20_07-21-47_from_jj"))

        with bu._log.invocation(bu.BFG.Push, parent=outer.iri) as c2:
            c2.emit(bu.BFG.subvol, bu.Literal("/d2/dev3"))
            parent_snap = c2.bn("parent_snapshot")
            c2.emit(bu.BFG.parentSnapshot, parent_snap)
            c2.emit_about(parent_snap, bu.BFG.abspath, bu.Literal("/bac20/.bfg_snapshots/dev3_2026-05-19_07-00-00_from_jj"))
            c2.emit(bu.BFG.bytesTransferred, bu.Literal(67108864, datatype=XSD.long))
            c2.emit(bu.BFG.bytesTransferred, bu.Literal(134217728, datatype=XSD.long))  # higher → MAX should win
            c2.emit(bu.BFG.pushedTo, bu.Literal("/bac20/backups/jj/.bfg_snapshots/dev3/dev3_2026-05-20_07-21-47_from_jj"))

    bu._print_backup_summary(bu._log, outer.iri)

    out = capsys.readouterr().out
    assert "backup summary" in out
    assert "LocalCommit" in out
    assert "Push" in out
    assert "/d2/dev3" in out
    assert "parent=/bac20/.bfg_snapshots/dev3_2026-05-19_07-00-00_from_jj" in out
    assert "bytes=134,217,728" in out  # max of the two emitted byte counts
    assert "→ /bac20/backups/jj/.bfg_snapshots/dev3/dev3_2026-05-20_07-21-47_from_jj" in out


def test_print_backup_summary_no_op_when_log_is_null(capsys):
    from schnabel import EventLog
    null_log = EventLog()
    assert null_log.is_null is True

    # Should not raise, should not print.
    bu = _fresh_backup_module_alt_path()
    bu._print_backup_summary(null_log, "urn:irrelevant")
    assert capsys.readouterr().out == ""


def _fresh_backup_module_alt_path():
    """Just import backup without mucking with env (for null-log tests)."""
    import hackery2.lib.backup as bu
    return bu
