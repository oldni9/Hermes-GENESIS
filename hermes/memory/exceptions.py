"""
===============================================================================
Hermes Memory Exceptions
===============================================================================
"""
from __future__ import annotations

class MemoryError(Exception):
    """Base exception for memory-related errors."""

class MemoryBackendError(MemoryError):
    """Raised when a memory backend operation fails."""

class MemoryEntryNotFoundError(MemoryError):
    """Raised when a memory entry is not found."""