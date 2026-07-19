"""
===============================================================================
Tests for Semantic Memory High-Level API
===============================================================================
"""
from __future__ import annotations

import pytest

from hermes.memory.semantic.semantic_memory import SemanticMemory
from hermes.memory.semantic.models import Document, SearchResult
from hermes.memory.semantic.exceptions import EmbeddingError, VectorStoreError


class DummyEmbeddingProvider:
    def embed(self, text: str) -> list[float]:
        return [0.1, 0.2]

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        return [[0.1, 0.2] for _ in texts]


class DummyVectorStore:
    def __init__(self):
        self.documents: dict[str, Document] = {}

    def add(self, document: Document) -> None:
        self.documents[document.id] = document

    def add_many(self, documents: list[Document]) -> None:
        for doc in documents:
            self.documents[doc.id] = doc

    def delete(self, document_id: str) -> None:
        self.documents.pop(document_id, None)

    def update(self, document: Document) -> None:
        self.documents[document.id] = document

    def get(self, document_id: str) -> Document | None:
        return self.documents.get(document_id)

    def exists(self, document_id: str) -> bool:
        return document_id in self.documents

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 10,
        score_threshold: float | None = None,
        metadata_filter: dict | None = None,
    ) -> list[SearchResult]:
        # Return SearchResult objects with dummy score
        docs = list(self.documents.values())
        if metadata_filter:
            docs = [d for d in docs if all(d.metadata.get(k) == v for k, v in metadata_filter.items())]
        # For simplicity, assign score 1.0 to all
        return [SearchResult(document=d, score=1.0) for d in docs[:top_k]]

    def clear(self) -> None:
        self.documents.clear()

    def count(self) -> int:
        return len(self.documents)


def test_semantic_memory_remember():
    embedding = DummyEmbeddingProvider()
    store = DummyVectorStore()
    memory = SemanticMemory(embedding, store)

    doc_id = memory.remember("test text", {"category": "test"})
    assert doc_id is not None
    assert store.count() == 1
    doc = store.documents[doc_id]
    assert doc.text == "test text"
    assert doc.metadata == {"category": "test"}
    assert doc.embedding == (0.1, 0.2)


def test_semantic_memory_remember_many():
    embedding = DummyEmbeddingProvider()
    store = DummyVectorStore()
    memory = SemanticMemory(embedding, store)

    texts = ["one", "two"]
    metadatas = [{"a": 1}, {"b": 2}]
    ids = memory.remember_many(texts, metadatas)
    assert len(ids) == 2
    assert store.count() == 2
    assert store.documents[ids[0]].text == "one"
    assert store.documents[ids[1]].text == "two"
    assert store.documents[ids[0]].metadata == {"a": 1}
    assert store.documents[ids[1]].metadata == {"b": 2}


def test_semantic_memory_add_alias():
    embedding = DummyEmbeddingProvider()
    store = DummyVectorStore()
    memory = SemanticMemory(embedding, store)

    doc_id = memory.add("test text")
    assert doc_id is not None
    assert store.count() == 1


def test_semantic_memory_search():
    embedding = DummyEmbeddingProvider()
    store = DummyVectorStore()
    memory = SemanticMemory(embedding, store)

    memory.remember("test one", {"category": "A"})
    memory.remember("test two", {"category": "B"})

    results = memory.search("test", metadata_filter={"category": "A"})
    assert len(results) == 1
    assert results[0].text == "test one"


def test_semantic_memory_delete():
    embedding = DummyEmbeddingProvider()
    store = DummyVectorStore()
    memory = SemanticMemory(embedding, store)

    doc_id = memory.remember("test")
    assert store.count() == 1
    memory.delete(doc_id)
    assert store.count() == 0


def test_semantic_memory_clear():
    embedding = DummyEmbeddingProvider()
    store = DummyVectorStore()
    memory = SemanticMemory(embedding, store)

    memory.remember("a")
    memory.remember("b")
    assert store.count() == 2
    memory.clear()
    assert store.count() == 0


def test_semantic_memory_count():
    embedding = DummyEmbeddingProvider()
    store = DummyVectorStore()
    memory = SemanticMemory(embedding, store)

    assert memory.count() == 0
    memory.remember("a")
    memory.remember("b")
    assert memory.count() == 2