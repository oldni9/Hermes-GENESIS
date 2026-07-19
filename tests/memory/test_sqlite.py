"""
===============================================================================
Tests for SQLite Memory Backend
===============================================================================
"""
from __future__ import annotations

import pytest

from hermes.memory.sqlite import SQLiteBackend
from hermes.memory.models import MemoryEntry


def test_sqlite_backend_add_search():
    backend = SQLiteBackend(":memory:")
    id1 = backend.add(MemoryEntry(content="hello world", metadata={"user": "alice"}))
    id2 = backend.add(MemoryEntry(content="goodbye world", metadata={"user": "bob"}))
    id3 = backend.add(MemoryEntry(content="hello again", metadata={"user": "alice"}))

    results = backend.search("hello")
    assert len(results) == 2
    assert results[0].content in ("hello again", "hello world")
    assert results[1].content in ("hello world", "hello again")
    assert results[0].metadata.get("user") == "alice"
    assert results[1].metadata.get("user") == "alice"


def test_sqlite_backend_delete():
    backend = SQLiteBackend(":memory:")
    entry = MemoryEntry(content="test")
    id1 = backend.add(entry)
    assert backend.delete(id1) is True
    assert backend.delete(id1) is False
    results = backend.search("test")
    assert len(results) == 0


def test_sqlite_backend_clear():
    backend = SQLiteBackend(":memory:")
    backend.add(MemoryEntry(content="a"))
    backend.add(MemoryEntry(content="b"))
    backend.clear()
    results = backend.search("")
    assert len(results) == 0


def test_sqlite_backend_persistent(tmp_path):
    db_file = tmp_path / "test.db"
    backend = SQLiteBackend(str(db_file))
    backend.add(MemoryEntry(content="persistent"))
    backend.close()

    # Reopen the same database file
    backend2 = SQLiteBackend(str(db_file))
    results = backend2.search("persistent")
    assert len(results) == 1
    assert results[0].content == "persistent"


def test_sqlite_backend_count():
    backend = SQLiteBackend(":memory:")
    assert backend.count() == 0
    backend.add(MemoryEntry(content="a"))
    backend.add(MemoryEntry(content="b"))
    assert backend.count() == 2


def test_sqlite_backend_context_manager(tmp_path):
    db_file = tmp_path / "test.db"
    with SQLiteBackend(str(db_file)) as backend:
        backend.add(MemoryEntry(content="context"))
    # After context exit, connection should be closed
    # Reopen and verify data persists
    backend2 = SQLiteBackend(str(db_file))
    results = backend2.search("context")
    assert len(results) == 1
    assert results[0].content == "context"