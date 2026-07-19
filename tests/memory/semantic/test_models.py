"""
===============================================================================
Tests for Semantic Memory Models
===============================================================================
"""
from __future__ import annotations

import time

from hermes.memory.semantic.models import Document, SearchResult


def test_document_creation():
    doc = Document(id="test-id", text="test text", metadata={"key": "value"}, embedding=(0.1, 0.2))
    assert doc.id == "test-id"
    assert doc.text == "test text"
    assert doc.metadata == {"key": "value"}
    assert doc.embedding == (0.1, 0.2)
    assert doc.created_at > 0


def test_document_immutable():
    doc = Document(id="test-id", text="test text")
    # Verify that the dataclass is frozen
    try:
        doc.text = "new text"  # type: ignore
        assert False, "Should have raised AttributeError"
    except AttributeError:
        pass


def test_document_serialization():
    doc = Document(id="test-id", text="test text", metadata={"a": 1}, embedding=(0.1, 0.2))
    data = doc.to_dict()
    assert data["id"] == "test-id"
    assert data["text"] == "test text"
    assert data["metadata"] == {"a": 1}
    assert data["embedding"] == [0.1, 0.2]

    doc2 = Document.from_dict(data)
    assert doc2.id == doc.id
    assert doc2.text == doc.text
    assert doc2.metadata == doc.metadata
    assert doc2.embedding == doc.embedding


def test_search_result():
    doc = Document(id="test-id", text="test")
    result = SearchResult(document=doc, score=0.95)
    assert result.document is doc
    assert result.score == 0.95