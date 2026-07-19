"""
===============================================================================
Semantic Memory Exceptions
===============================================================================
"""
from __future__ import annotations


class MemoryError(Exception):
    """Base exception for memory-related errors."""


class EmbeddingError(MemoryError):
    """Raised when an embedding operation fails."""


class VectorStoreError(MemoryError):
    """Raised when a vector store operation fails."""


class RetrievalError(MemoryError):
    """Raised when retrieval fails."""