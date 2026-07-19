"""
===============================================================================
Semantic Memory High-Level API
===============================================================================
"""
from __future__ import annotations

import uuid
from typing import Any, Dict, List, Mapping, Optional

from .interfaces import EmbeddingProvider, VectorStore
from .models import Document, SearchResult
from .retriever import Retriever
from .exceptions import EmbeddingError, VectorStoreError


class SemanticMemory:
    """
    High-level API for semantic memory.
    Uses dependency injection for embedding and vector store.
    """

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
    ) -> None:
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store
        self._retriever = Retriever(embedding_provider, vector_store)

    def remember(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Store a text in memory.
        Returns the document ID.
        """
        try:
            embedding = self._embedding_provider.embed(text)
        except EmbeddingError:
            raise
        except Exception as e:
            raise EmbeddingError(f"Failed to generate embedding: {e}") from e

        doc_id = str(uuid.uuid4())
        document = Document(
            id=doc_id,
            text=text,
            metadata=metadata or {},
            embedding=tuple(embedding),
        )
        try:
            self._vector_store.add(document)
        except VectorStoreError:
            raise
        except Exception as e:
            raise VectorStoreError(f"Failed to add document to vector store: {e}") from e

        return doc_id

    def remember_many(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> List[str]:
        """
        Store multiple texts in memory.
        Returns a list of document IDs.
        """
        if metadatas is None:
            metadatas = [{} for _ in texts]
        if len(texts) != len(metadatas):
            raise ValueError("Number of texts and metadatas must match.")

        try:
            embeddings = self._embedding_provider.embed_many(texts)
        except EmbeddingError:
            raise
        except Exception as e:
            raise EmbeddingError(f"Failed to generate embeddings: {e}") from e

        documents = []
        for i, text in enumerate(texts):
            doc_id = str(uuid.uuid4())
            document = Document(
                id=doc_id,
                text=text,
                metadata=metadatas[i],
                embedding=tuple(embeddings[i]),
            )
            documents.append(document)

        try:
            self._vector_store.add_many(documents)
        except VectorStoreError:
            raise
        except Exception as e:
            raise VectorStoreError(f"Failed to add documents to vector store: {e}") from e

        return [doc.id for doc in documents]

    def add(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Alias for remember()."""
        return self.remember(text, metadata)

    def add_many(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        """Alias for remember_many()."""
        return self.remember_many(texts, metadatas)

    def search(
        self,
        query: str,
        top_k: int = 10,
        score_threshold: Optional[float] = None,
        metadata_filter: Optional[Mapping[str, Any]] = None,
    ) -> List[Document]:
        """
        Search for documents relevant to the query.
        """
        return self._retriever.retrieve(
            query=query,
            top_k=top_k,
            score_threshold=score_threshold,
            metadata_filter=metadata_filter,
        )

    def search_with_scores(
        self,
        query: str,
        top_k: int = 10,
        score_threshold: Optional[float] = None,
        metadata_filter: Optional[Mapping[str, Any]] = None,
    ) -> List[SearchResult]:
        """
        Search for documents and return scores.
        """
        return self._retriever.search_with_scores(
            query=query,
            top_k=top_k,
            score_threshold=score_threshold,
            metadata_filter=metadata_filter,
        )

    def delete(self, document_id: str) -> None:
        """
        Delete a document from memory.
        """
        try:
            self._vector_store.delete(document_id)
        except VectorStoreError:
            raise
        except Exception as e:
            raise VectorStoreError(f"Failed to delete document: {e}") from e

    def clear(self) -> None:
        """
        Clear all documents from memory.
        """
        try:
            self._vector_store.clear()
        except VectorStoreError:
            raise
        except Exception as e:
            raise VectorStoreError(f"Failed to clear vector store: {e}") from e

    def count(self) -> int:
        """
        Return the number of documents in memory.
        """
        try:
            return self._vector_store.count()
        except VectorStoreError:
            raise
        except Exception as e:
            raise VectorStoreError(f"Failed to count documents: {e}") from e