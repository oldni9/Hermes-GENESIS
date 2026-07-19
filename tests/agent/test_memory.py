"""
===============================================================================
Tests for Agent Memory Integration
===============================================================================
"""
from __future__ import annotations

import pytest

from hermes.agent.memory import AgentMemory
from hermes.memory.in_memory import InMemoryBackend
from hermes.memory.sqlite import SQLiteBackend
from hermes.memory.models import MemoryEntry


def test_agent_memory_default_backend():
    memory = AgentMemory()
    assert isinstance(memory.backend, InMemoryBackend)


def test_agent_memory_with_custom_backend():
    backend = SQLiteBackend(":memory:")
    memory = AgentMemory(backend=backend)
    assert memory.backend is backend


def test_agent_memory_add_search():
    memory = AgentMemory()
    memory.add("hello", tags=("greeting",), metadata={"user": "alice"})
    memory.add("world", tags=("planet",))
    results = memory.search("hello")
    assert len(results) == 1
    assert results[0].content == "hello"
    # Tags are stored as tuple, so they are not directly in metadata
    # They are in the MemoryEntry.tags field.
    # We can verify they are present as a tuple.
    assert results[0].tags == ("greeting",)
    assert results[0].metadata.get("user") == "alice"


def test_agent_memory_delete():
    memory = AgentMemory()
    id1 = memory.add("test")
    assert memory.delete(id1) is True
    assert memory.delete(id1) is False
    assert memory.search("test") == []


def test_agent_memory_clear():
    memory = AgentMemory()
    memory.add("a")
    memory.add("b")
    memory.clear()
    assert memory.search("") == []


def test_agent_memory_count():
    memory = AgentMemory()
    assert memory.count() == 0
    memory.add("a")
    memory.add("b")
    assert memory.count() == 2


def test_agent_memory_len():
    memory = AgentMemory()
    assert len(memory) == 0
    memory.add("a")
    memory.add("b")
    assert len(memory) == 2


def test_agent_memory_close():
    memory = AgentMemory()
    backend = SQLiteBackend(":memory:")
    memory = AgentMemory(backend=backend)
    memory.add("test")
    memory.close()
    # After close, the backend should be closed; reusing might fail, but we just test close exists.
    assert memory.backend is backend