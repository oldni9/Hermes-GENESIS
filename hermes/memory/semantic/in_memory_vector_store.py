"""
===============================================================================
In-Memory Vector Store
===============================================================================
"""
from __future__ import annotations

import math
from typing import Dict, List, Mapping, Optional

from .interfaces import VectorStore
from .models import Document, SearchResult
from .exceptions import VectorStoreError


class InMemoryVectorStore(VectorStore):
    """
    In-memory vector store implementation.
    Uses cosine similarity for scoring.
    """

    def __init__(self) -> None:
        self._documents: Dict[str, Document] = {}

    def add(self, document: Document) -> None:
        if document.id in self._documents:
            raise VectorStoreError(f"Document with ID {document.id} already exists.")
        self._documents[document.id] = document

    def add_many(self, documents: List[Document]) -> None:
        # Validate all documents first to ensure atomicity
        for doc in documents:
            if doc.id in self._documents:
                raise VectorStoreError(f"Document with ID {doc.id} already exists.")
        # Then insert
        for doc in documents:
            self._documents[doc.id] = doc

    def delete(self, document_id: str) -> None:
        if document_id not in self._documents:
            raise VectorStoreError(f"Document with ID {document_id} not found.")
        del self._documents[document_id]

    def update(self, document: Document) -> None:
        if document.id not in self._documents:
            raise VectorStoreError(f"Document with ID {document.id} not found.")
        self._documents[document.id] = document

    def get(self, document_id: str) -> Document | None:
        return self._documents.get(document_id)

    def exists(self, document_id: str) -> bool:
        return document_id in self._documents

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        score_threshold: Optional[float] = None,
        metadata_filter: Optional[Mapping[str, Any]] = None,
    ) -> List[SearchResult]:
        results: List[SearchResult] = []
        for doc in self._documents.values():
            if doc.embedding is None:
                continue
            if metadata_filter:
                if not all(doc.metadata.get(k) == v for k, v in metadata_filter.items()):
                    continue
            score = self._cosine_similarity(query_embedding, list(doc.embedding))
            # Skip invalid scores instead of raising
            if math.isnan(score) or math.isinf(score):
                continue
            if score_threshold is not None and score < score_threshold:
                continue
            results.append(SearchResult(document=doc, score=score))
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]

    def clear(self) -> None:
        self._documents.clear()

    def count(self) -> int:
        return len(self._documents)