"""
===============================================================================
Tests for In-Memory Vector Store
===============================================================================
"""
from __future__ import annotations

import math
import pytest

from hermes.memory.semantic.in_memory_vector_store import InMemoryVectorStore
from hermes.memory.semantic.models import Document
from hermes.memory.semantic.exceptions import VectorStoreError


def test_add_and_search():
    store = InMemoryVectorStore()
    doc1 = Document(id="1", text="a", embedding=(0.1, 0.2))
    doc2 = Document(id="2", text="b", embedding=(0.3, 0.4))
    store.add(doc1)
    store.add(doc2)

    results = store.search([0.1, 0.2], top_k=2)
    assert len(results) == 2
    assert results[0].document.id == "1"
    assert results[0].score >= results[1].score


def test_add_many_atomic():
    store = InMemoryVectorStore()
    doc1 = Document(id="1", text="a")
    doc2 = Document(id="2", text="b")
    doc3 = Document(id="1", text="c")  # duplicate
    store.add(doc1)
    with pytest.raises(VectorStoreError, match="already exists"):
        store.add_many([doc2, doc3])
    # doc2 should not have been added because of duplicate
    assert store.count() == 1


def test_delete():
    store = InMemoryVectorStore()
    doc = Document(id="1", text="a")
    store.add(doc)
    assert store.exists("1")
    store.delete("1")
    assert not store.exists("1")
    with pytest.raises(VectorStoreError, match="not found"):
        store.delete("1")


def test_update():
    store = InMemoryVectorStore()
    doc1 = Document(id="1", text="a")
    store.add(doc1)
    doc2 = Document(id="1", text="b")
    store.update(doc2)
    assert store.get("1").text == "b"
    with pytest.raises(VectorStoreError, match="not found"):
        store.update(Document(id="2", text="c"))


def test_get():
    store = InMemoryVectorStore()
    doc = Document(id="1", text="a")
    store.add(doc)
    assert store.get("1") is doc
    assert store.get("2") is None


def test_exists():
    store = InMemoryVectorStore()
    doc = Document(id="1", text="a")
    store.add(doc)
    assert store.exists("1")
    assert not store.exists("2")


def test_search_metadata_filter():
    store = InMemoryVectorStore()
    doc1 = Document(id="1", text="a", metadata={"cat": "A"}, embedding=(0.1, 0.2))
    doc2 = Document(id="2", text="b", metadata={"cat": "B"}, embedding=(0.3, 0.4))
    store.add(doc1)
    store.add(doc2)

    results = store.search([0.1, 0.2], metadata_filter={"cat": "A"})
    assert len(results) == 1
    assert results[0].document.id == "1"


def test_search_score_threshold():
    store = InMemoryVectorStore()
    doc1 = Document(id="1", text="a", embedding=(1.0, 0.0))
    doc2 = Document(id="2", text="b", embedding=(0.5, 0.5))
    store.add(doc1)
    store.add(doc2)

    results = store.search([1.0, 0.0], score_threshold=0.8)
    assert len(results) == 1
    assert results[0].document.id == "1"


def test_search_handles_nan_inf():
    store = InMemoryVectorStore()
    doc1 = Document(id="1", text="a", embedding=(float("nan"), 0.0))
    doc2 = Document(id="2", text="b", embedding=(float("inf"), 0.0))
    doc3 = Document(id="3", text="c", embedding=(1.0, 0.0))
    store.add(doc1)
    store.add(doc2)
    store.add(doc3)

    # Search should skip NaN/inf and still return valid results
    results = store.search([1.0, 0.0])
    assert len(results) == 1
    assert results[0].document.id == "3"


def test_clear():
    store = InMemoryVectorStore()
    store.add(Document(id="1", text="a"))
    store.add(Document(id="2", text="b"))
    assert store.count() == 2
    store.clear()
    assert store.count() == 0