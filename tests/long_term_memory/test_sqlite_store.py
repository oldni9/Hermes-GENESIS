"""
===============================================================================
Tests for SQLite Store
===============================================================================
"""

import pytest
import os
import tempfile
import time
import datetime

from hermes.long_term_memory.sqlite_store import SQLiteStore


@pytest.fixture
def store():
    with SQLiteStore(":memory:") as store:
        yield store

def test_implements_memory_store_interface(store):
    """Verify that SQLiteStore implements the same API as MemoryStore."""
    assert hasattr(store, "add")
    assert hasattr(store, "update")
    assert hasattr(store, "delete")
    assert hasattr(store, "clear")
    assert hasattr(store, "get")
    assert hasattr(store, "list")
    assert hasattr(store, "search")

def test_add_record(store):
    record = store.add("Test content", {"author": "test"})
    assert record.id is not None
    assert record.content == "Test content"
    assert record.metadata == {"author": "test"}
    assert record in store.list()

def test_add_empty_metadata(store):
    record = store.add("Test content", None)
    assert record.metadata == {}

def test_add_unserializable_metadata(store):
    """Test that unserializable metadata (like datetime) doesn't crash."""
    record = store.add("Test content", {"date": datetime.datetime.now()})
    assert record.id is not None
    fetched = store.get(record.id)
    assert isinstance(fetched.metadata["date"], str)

def test_update_record_merges_metadata(store):
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
    r1 = store.add("First")
    time.sleep(0.01)
    r2 = store.add("Second")
    time.sleep(0.01)
    r3 = store.add("Third")
    
    records = store.list()
    assert len(records) == 3
    assert records[0].id == r1.id
    assert records[1].id == r2.id
    assert records[2].id == r3.id

def test_search_deterministic_order(store):
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

def test_search_escapes_wildcards(store):
    """Test that literal % and _ characters are escaped in search."""
    store.add("Progress: 100%")
    store.add("Special_Char")
    
    # Search for literal '%'
    results = store.search("100%")
    assert len(results) == 1
    assert results[0].content == "Progress: 100%"
    
    # Search for literal '_'
    results = store.search("Special_")
    assert len(results) == 1
    assert results[0].content == "Special_Char"

def test_persistence_across_reconnects():
    """Test that data persists when the database is closed and reopened."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_memory.db")
        
        store1 = SQLiteStore(db_path)
        record = store1.add("Persistent memory", {"author": "test"})
        store1.close()
        
        store2 = SQLiteStore(db_path)
        fetched = store2.get(record.id)
        assert fetched is not None
        assert fetched.content == "Persistent memory"
        assert fetched.metadata == {"author": "test"}
        store2.close()

def test_schema_versioning_migration(store):
    """Test that the schema_migrations table is created and populated."""
    cursor = store._conn.execute("SELECT version FROM schema_migrations WHERE version = 1;")
    row = cursor.fetchone()
    assert row is not None
    assert row[0] == 1

def test_close_twice(store):
    """Test that closing the store multiple times does not raise an error."""
    store.close()
    store.close()  # Should be idempotent

def test_operations_after_close(store):
    """Test that operations after close raise a RuntimeError."""
    store.close()
    with pytest.raises(RuntimeError, match="SQLiteStore has been closed."):
        store.add("Test")
        
    with pytest.raises(RuntimeError, match="SQLiteStore has been closed."):
        store.search("Test")

def test_context_manager_closes():
    """Test that exiting the context manager closes the connection."""
    with SQLiteStore(":memory:") as store:
        pass

    with pytest.raises(RuntimeError, match="SQLiteStore has been closed."):
        store.add("x")