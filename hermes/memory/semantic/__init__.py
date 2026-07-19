"""
===============================================================================
Semantic Memory Package
===============================================================================
"""
from __future__ import annotations

from .models import Document, SearchResult
from .interfaces import EmbeddingProvider, VectorStore
from .retriever import Retriever
from .semantic_memory import SemanticMemory
from .exceptions import MemoryError, EmbeddingError, VectorStoreError, RetrievalError
from .in_memory_vector_store import InMemoryVectorStore

__all__ = [
    "Document",
    "SearchResult",
    "EmbeddingProvider",
    "VectorStore",
    "Retriever",
    "SemanticMemory",
    "MemoryError",
    "EmbeddingError",
    "VectorStoreError",
    "RetrievalError",
    "InMemoryVectorStore",
]