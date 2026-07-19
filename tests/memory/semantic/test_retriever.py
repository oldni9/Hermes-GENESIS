"""
===============================================================================
Tests for Semantic Retriever
===============================================================================
"""
from __future__ import annotations

import pytest

from hermes.memory.semantic.retriever import Retriever
from hermes.memory.semantic.models import Document, SearchResult
from hermes.memory.semantic.exceptions import RetrievalError


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
        # Return stored documents with a dummy score
        results = []
        for doc in self.documents.values():
            if metadata_filter:
                if not all(doc.metadata.get(k) == v for k, v in metadata_filter.items()):
                    continue
            results.append(SearchResult(document=doc, score=1.0))
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]

    def clear(self) -> None:
        self.documents.clear()

    def count(self) -> int:
        return len(self.documents)


def test_retriever_single():
    embedding_provider = DummyEmbeddingProvider()
    vector_store = DummyVectorStore()
    retriever = Retriever(embedding_provider, vector_store)

    doc = Document(id="1", text="test", embedding=[0.1, 0.2])
    vector_store.add(doc)

    results = retriever.retrieve("query")
    assert len(results) == 1
    assert results[0].id == "1"


def test_retriever_many():
    embedding_provider = DummyEmbeddingProvider()
    vector_store = DummyVectorStore()
    retriever = Retriever(embedding_provider, vector_store)

    docs = [
        Document(id="1", text="one", embedding=[0.1, 0.2]),
        Document(id="2", text="two", embedding=[0.2, 0.3]),
    ]
    vector_store.add_many(docs)

    results = retriever.retrieve_many(["query1", "query2"])
    assert len(results) == 2
    assert len(results[0]) == 2
    assert len(results[1]) == 2


def test_retriever_metadata_filter():
    embedding_provider = DummyEmbeddingProvider()
    vector_store = DummyVectorStore()
    retriever = Retriever(embedding_provider, vector_store)

    docs = [
        Document(id="1", text="one", metadata={"category": "A"}),
        Document(id="2", text="two", metadata={"category": "B"}),
    ]
    vector_store.add_many(docs)

    # We expect that the vector store's search method will filter by metadata.
    # The dummy store already implements metadata_filter support, so this should work.
    results = retriever.retrieve(
        "query",
        metadata_filter={"category": "A"},
    )
    assert len(results) == 1
    assert results[0].id == "1"