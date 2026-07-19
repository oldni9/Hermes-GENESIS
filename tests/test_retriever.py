"""
===============================================================================
Tests for Knowledge Retriever
===============================================================================
"""

from __future__ import annotations

import pytest

from hermes.knowledge.document import KnowledgeDocument
from hermes.knowledge.index import KnowledgeIndex
from hermes.knowledge.retriever import KnowledgeRetriever


class TestKnowledgeRetriever:
    def test_retrieve(self):
        index = KnowledgeIndex()
        doc = KnowledgeDocument(id="1", title="Test", content="Content")
        index.add(doc)
        retriever = KnowledgeRetriever(index)
        results = retriever.retrieve("Test")
        assert len(results) == 1
        assert results[0].id == "1"

    def test_retrieve_with_scores(self):
        index = KnowledgeIndex()
        doc = KnowledgeDocument(id="1", title="Test", content="Content")
        index.add(doc)
        retriever = KnowledgeRetriever(index)
        results = retriever.retrieve_with_scores("Test")
        assert len(results) == 1
        doc_result, score = results[0]
        assert doc_result.id == "1"
        assert score > 0

    def test_retrieve_by_id(self):
        index = KnowledgeIndex()
        doc = KnowledgeDocument(id="1", title="Test", content="Content")
        index.add(doc)
        retriever = KnowledgeRetriever(index)
        retrieved = retriever.retrieve_by_id("1")
        assert retrieved is not None
        assert retrieved.id == "1"
        assert retriever.retrieve_by_id("missing") is None