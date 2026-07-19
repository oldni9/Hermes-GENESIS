"""
===============================================================================
Tests for Memory Backend Protocol
===============================================================================
"""
from __future__ import annotations

import pytest

from hermes.memory.backend import MemoryBackend, MemoryCapabilities
from hermes.memory.in_memory import InMemoryBackend
from hermes.memory.sqlite import SQLiteBackend
from hermes.memory.models import MemoryEntry


class DummyBackend:
    """Minimal implementation for protocol testing."""
    @property
    def capabilities(self) -> MemoryCapabilities:
        return MemoryCapabilities()

    def add(self, entry: MemoryEntry) -> str:
        return "dummy-id"

    def search(self, query: str, limit: int = 10) -> list:
        return []

    def count(self) -> int:
        return 0

    def delete(self, entry_id: str) -> bool:
        return False

    def clear(self) -> None:
        pass

    def close(self) -> None:
        pass


def test_memory_backend_protocol():
    backend = DummyBackend()
    assert isinstance(backend, MemoryBackend)
    assert backend.capabilities.persistent is False
    assert backend.capabilities.semantic_search is False
    assert backend.capabilities.delete is True
    assert backend.capabilities.metadata_filtering is False


def test_memory_capabilities():
    caps = MemoryCapabilities(persistent=True, semantic_search=True)
    assert caps.persistent is True
    assert caps.semantic_search is True
    assert caps.delete is True


def test_backend_protocol_conformance():
    backends = [
        InMemoryBackend(),
        SQLiteBackend(":memory:"),
    ]
    for backend in backends:
        assert isinstance(backend, MemoryBackend)
        assert hasattr(backend, "capabilities")
        assert hasattr(backend, "add")
        assert hasattr(backend, "search")
        assert hasattr(backend, "count")
        assert hasattr(backend, "delete")
        assert hasattr(backend, "clear")
        assert hasattr(backend, "close")


def test_backend_does_not_mutate_caller_entry():
    backend = InMemoryBackend()
    original = MemoryEntry(content="test", tags=("a",))
    before_timestamp = original.timestamp
    backend.add(original)

    # original should remain unchanged
    assert original.id == ""
    assert original.timestamp == before_timestamp
    # The backend should have created a new entry
    results = backend.search("test")
    assert len(results) == 1
    assert results[0].id != ""
    assert results[0].timestamp >= before_timestamp


def test_memory_entry_equality():
    # Two entries with the same content, tags, metadata, and timestamp should be equal.
    entry1 = MemoryEntry(
        id="",
        content="test",
        tags=("a", "b"),
        timestamp=123.0,
        metadata={"key": "value"},
    )
    entry2 = MemoryEntry(
        id="",
        content="test",
        tags=("a", "b"),
        timestamp=123.0,
        metadata={"key": "value"},
    )
    assert entry1 == entry2
    # Different content should not be equal
    entry3 = MemoryEntry(content="different")
    assert entry1 != entry3