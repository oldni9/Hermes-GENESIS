"""
===============================================================================
Tests for Memory Manager
===============================================================================
"""

import pytest
from hermes.long_term_memory.manager import MemoryManager
from hermes.long_term_memory.store import MemoryStore


@pytest.fixture
def manager():
    return MemoryManager(store=MemoryStore())


def test_add_validation_empty_content(manager):
    with pytest.raises(ValueError, match="Memory content cannot be empty."):
        manager.add("   ")

def test_add_validation_not_string(manager):
    with pytest.raises(ValueError):
        manager.add(123) # type: ignore

def test_search_validation_not_string(manager):
    with pytest.raises(ValueError, match="Search query must be a string."):
        manager.search(123) # type: ignore

def test_delegation_add_and_get(manager):
    record = manager.add("Test")
    assert manager.get(record.id).content == "Test"

def test_delegation_update(manager):
    record = manager.add("Test")
    updated = manager.update(record.id, "Updated")
    assert updated.content == "Updated"

def test_delegation_delete(manager):
    record = manager.add("Test")
    assert manager.delete(record.id) is True
    assert manager.get(record.id) is None

def test_delegation_clear(manager):
    manager.add("A")
    manager.clear()
    assert len(manager.list()) == 0