"""
===============================================================================
Tests for Memory Store
===============================================================================
"""

import pytest
from hermes.long_term_memory.store import MemoryStore
from hermes.long_term_memory.models import MemoryRecord


@pytest.fixture
def store():
    return MemoryStore()


def test_add_record(store):
    record = store.add("Test content", {"author": "test"})
    assert record.id is not None
    assert record.content == "Test content"
    assert record.metadata == {"author": "test"}
    assert record in store.list()


def test_add_empty_metadata(store):
    record = store.add("Test content", None)
    assert record.metadata == {}


def test_update_record(store):
    record = store.add("Initial", {"key": "value"})
    updated = store.update(record.id, content="Updated", metadata={"key2": "value2"})
    
    assert updated is not None
    assert updated.content == "Updated"
    assert updated.metadata == {"key": "value", "key2": "value2"}
    assert updated.updated_at >= record.created_at

def test_update_nonexistent(store):
    assert store.update("nonexistent-id", "content") is None

def test_delete_record(store):
    record = store.add("To be deleted")
    assert store.delete(record.id) is True
    assert store.get(record.id) is None

def test_delete_nonexistent(store):
    assert store.delete("nonexistent-id") is False

def test_clear_records(store):
    store.add("A")
    store.add("B")
    store.clear()
    assert len(store.list()) == 0

def test_get_record(store):
    record = store.add("Get me")
    assert store.get(record.id).content == "Get me"

def test_list_deterministic_order(store):
    import time
    r1 = store.add("First")
    time.sleep(0.01)
    r2 = store.add("Second")
    time.sleep(0.01)
    r3 = store.add("Third")
    
    records = store.list()
    assert records[0].id == r1.id
    assert records[1].id == r2.id
    assert records[2].id == r3.id

def test_search_deterministic_order(store):
    import time
    r1 = store.add("Find this string")
    time.sleep(0.01)
    r2 = store.add("Also find this string")
    
    results = store.search("find")
    assert len(results) == 2
    assert results[0].id == r1.id
    assert results[1].id == r2.id

def test_search_case_insensitive(store):
    store.add("Mixed Case String")
    results = store.search("mixed case")
    assert len(results) == 1