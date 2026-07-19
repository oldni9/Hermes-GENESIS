"""
===============================================================================
Semantic Retriever
===============================================================================
"""
from __future__ import annotations

from typing import Any, List, Mapping, Optional

from .interfaces import EmbeddingProvider, VectorStore
from .models import Document, SearchResult
from .exceptions import EmbeddingError, VectorStoreError


class Retriever:
    """
    Retriever that uses an embedding provider and a vector store.
    Supports top-k, score threshold, and metadata filtering.
    """

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
    ) -> None:
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store

    def _search_with_scores(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        score_threshold: Optional[float] = None,
        metadata_filter: Optional[Mapping[str, Any]] = None,
    ) -> List[SearchResult]:
        """
        Internal search method returning SearchResult objects.
        """
        try:
            results = self._vector_store.search(
                query_embedding=query_embedding,
                top_k=top_k,
                score_threshold=score_threshold,
                metadata_filter=metadata_filter,
            )
        except VectorStoreError:
            raise
        except Exception as e:
            raise VectorStoreError(f"Vector store search failed: {e}") from e
        return results

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        score_threshold: Optional[float] = None,
        metadata_filter: Optional[Mapping[str, Any]] = None,
    ) -> List[Document]:
        """
        Retrieve documents relevant to the query.
        """
        try:
            query_embedding = self._embedding_provider.embed(query)
        except EmbeddingError:
            raise
        except Exception as e:
            raise EmbeddingError(f"Embedding failed: {e}") from e

        results = self._search_with_scores(
            query_embedding=query_embedding,
            top_k=top_k,
            score_threshold=score_threshold,
            metadata_filter=metadata_filter,
        )
        return [result.document for result in results]

    def retrieve_many(
        self,
        queries: List[str],
        top_k: int = 10,
        score_threshold: Optional[float] = None,
        metadata_filter: Optional[Mapping[str, Any]] = None,
    ) -> List[List[Document]]:
        """
        Retrieve documents for multiple queries.
        """
        try:
            query_embeddings = self._embedding_provider.embed_many(queries)
        except EmbeddingError:
            raise
        except Exception as e:
            raise EmbeddingError(f"Embedding failed: {e}") from e

        results = []
        for embedding in query_embeddings:
            docs = self._search_with_scores(
                query_embedding=embedding,
                top_k=top_k,
                score_threshold=score_threshold,
                metadata_filter=metadata_filter,
            )
            results.append([result.document for result in docs])
        return results

    def search_with_scores(
        self,
        query: str,
        top_k: int = 10,
        score_threshold: Optional[float] = None,
        metadata_filter: Optional[Mapping[str, Any]] = None,
    ) -> List[SearchResult]:
        """
        Search and return documents with similarity scores.
        """
        try:
            query_embedding = self._embedding_provider.embed(query)
        except EmbeddingError:
            raise
        except Exception as e:
            raise EmbeddingError(f"Embedding failed: {e}") from e

        return self._search_with_scores(
            query_embedding=query_embedding,
            top_k=top_k,
            score_threshold=score_threshold,
            metadata_filter=metadata_filter,
        )