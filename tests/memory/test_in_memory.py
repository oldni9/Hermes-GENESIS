"""
===============================================================================
Tests for In-Memory Memory Backend
===============================================================================
"""
from __future__ import annotations

import pytest

from hermes.memory.in_memory import InMemoryBackend
from hermes.memory.models import MemoryEntry


def test_in_memory_backend_add_search():
    backend = InMemoryBackend()
    id1 = backend.add(MemoryEntry(content="hello world", metadata={"user": "alice"}))
    id2 = backend.add(MemoryEntry(content="goodbye world", metadata={"user": "bob"}))
    id3 = backend.add(MemoryEntry(content="hello again", metadata={"user": "alice"}))

    results = backend.search("hello")
    assert len(results) == 2
    assert results[0].content in ("hello again", "hello world")
    assert results[1].content in ("hello world", "hello again")
    # Metadata should be preserved
    assert results[0].metadata.get("user") == "alice"
    assert results[1].metadata.get("user") == "alice"


def test_in_memory_backend_delete():
    backend = InMemoryBackend()
    entry = MemoryEntry(content="test")
    id1 = backend.add(entry)
    assert backend.delete(id1) is True
    assert backend.delete(id1) is False
    results = backend.search("test")
    assert len(results) == 0


def test_in_memory_backend_clear():
    backend = InMemoryBackend()
    backend.add(MemoryEntry(content="a"))
    backend.add(MemoryEntry(content="b"))
    assert len(backend._entries) == 2
    backend.clear()
    assert len(backend._entries) == 0


def test_in_memory_backend_count():
    backend = InMemoryBackend()
    assert backend.count() == 0
    backend.add(MemoryEntry(content="a"))
    backend.add(MemoryEntry(content="b"))
    assert backend.count() == 2