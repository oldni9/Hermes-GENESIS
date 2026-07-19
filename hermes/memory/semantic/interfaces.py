"""
===============================================================================
Semantic Memory Interfaces
===============================================================================
"""
from __future__ import annotations

from typing import Any, List, Mapping, Optional, Protocol, runtime_checkable

from .models import Document, SearchResult


@runtime_checkable
class EmbeddingProvider(Protocol):
    """
    Protocol for embedding providers.
    """

    def embed(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        Returns a list of floats.
        Raises EmbeddingError on failure.
        """
        ...

    def embed_many(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        Returns a list of embeddings.
        Raises EmbeddingError on failure.
        """
        ...


@runtime_checkable
class VectorStore(Protocol):
    """
    Protocol for vector stores.
    """

    def add(self, document: Document) -> None:
        """
        Add a document to the store.
        Raises VectorStoreError if a document with the same ID already exists.
        """
        ...

    def add_many(self, documents: List[Document]) -> None:
        """
        Add multiple documents to the store.
        If any document fails (e.g., duplicate ID), the entire operation should roll back.
        Implementations should either validate all documents first or use a transaction.
        Raises VectorStoreError on failure.
        """
        ...

    def delete(self, document_id: str) -> None:
        """
        Delete a document by ID.
        Raises VectorStoreError if not found.
        """
        ...

    def update(self, document: Document) -> None:
        """
        Update an existing document.
        The document's ID must exist in the store.
        Raises VectorStoreError if not found.
        """
        ...

    def get(self, document_id: str) -> Document | None:
        """
        Retrieve a document by ID.
        Returns None if not found.
        """
        ...

    def exists(self, document_id: str) -> bool:
        """
        Check if a document exists by ID.
        """
        ...

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        score_threshold: Optional[float] = None,
        metadata_filter: Optional[Mapping[str, Any]] = None,
    ) -> List[SearchResult]:
        """
        Search for documents by embedding.
        Returns a list of SearchResult objects ordered by score (highest first).
        Raises VectorStoreError on failure.
        """
        ...

    def clear(self) -> None:
        """
        Remove all documents from the store.
        Raises VectorStoreError on failure.
        """
        ...

    def count(self) -> int:
        """
        Return the number of documents in the store.
        Raises VectorStoreError on failure.
        """
        ...