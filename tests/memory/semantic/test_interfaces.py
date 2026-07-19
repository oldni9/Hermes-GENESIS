"""
===============================================================================
Tests for Semantic Memory Interfaces
===============================================================================
"""
from __future__ import annotations

from hermes.memory.semantic.interfaces import EmbeddingProvider, VectorStore
from hermes.memory.semantic.models import Document


class DummyEmbeddingProvider:
    def embed(self, text: str) -> list[float]:
        return [0.1, 0.2, 0.3]

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        return [[0.1, 0.2, 0.3] for _ in texts]


class DummyVectorStore:
    def __init__(self):
        self._docs: dict[str, Document] = {}

    def add(self, document: Document) -> None:
        self._docs[document.id] = document

    def add_many(self, documents: list[Document]) -> None:
        for doc in documents:
            self._docs[doc.id] = doc

    def delete(self, document_id: str) -> None:
        self._docs.pop(document_id, None)

    def update(self, document: Document) -> None:
        self._docs[document.id] = document

    def get(self, document_id: str) -> Document | None:
        return self._docs.get(document_id)

    def exists(self, document_id: str) -> bool:
        return document_id in self._docs

    def search(self, query_embedding: list[float], top_k: int = 10, score_threshold: float | None = None, metadata_filter: dict | None = None) -> list:
        return []

    def clear(self) -> None:
        self._docs.clear()

    def count(self) -> int:
        return len(self._docs)


def test_embedding_provider_protocol():
    provider = DummyEmbeddingProvider()
    assert isinstance(provider, EmbeddingProvider)
    embedding = provider.embed("test")
    assert len(embedding) == 3
    embeddings = provider.embed_many(["a", "b"])
    assert len(embeddings) == 2
    assert len(embeddings[0]) == 3


def test_vector_store_protocol():
    store = DummyVectorStore()
    assert isinstance(store, VectorStore)
    doc = Document(id="1", text="test")
    store.add(doc)
    assert store.exists("1")
    assert store.get("1") is doc
    assert store.count() == 1
    store.delete("1")
    assert not store.exists("1")