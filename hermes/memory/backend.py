"""
===============================================================================
Hermes Memory Backend Protocol
===============================================================================
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from .models import MemoryEntry


@dataclass(slots=True)
class MemoryCapabilities:
    """
    Describes the capabilities of a memory backend.
    """
    persistent: bool = False
    semantic_search: bool = False
    delete: bool = True
    metadata_filtering: bool = False


@runtime_checkable
class MemoryBackend(Protocol):
    """
    Protocol for all memory backends.
    Storage implementations must satisfy this protocol.
    """

    @property
    def capabilities(self) -> MemoryCapabilities:
        """Return the capabilities of this backend."""
        ...

    def add(self, entry: MemoryEntry) -> str:
        """
        Add a new memory entry.
        The backend is responsible for assigning persistent identity and storage metadata.
        The supplied entry must be treated as immutable;
        implementations must not mutate the caller's object.
        Returns the entry's ID.
        Raises MemoryError on failure.
        """
        ...

    def search(self, query: str, limit: int = 10) -> list[MemoryEntry]:
        """
        Search for memory entries matching the query.
        Results are ordered by score (descending), then by timestamp (descending).
        Returns a list of MemoryEntry objects.
        Raises MemoryError on failure.
        """
        ...

    def count(self) -> int:
        """
        Return the total number of entries in the backend.
        Raises MemoryError on failure.
        """
        ...

    def delete(self, entry_id: str) -> bool:
        """
        Delete a memory entry by ID.
        Returns True if deleted, False if not found.
        Raises MemoryError on failure.
        """
        ...

    def clear(self) -> None:
        """
        Clear all memory entries.
        Raises MemoryError on failure.
        """
        ...

    def close(self) -> None:
        """
        Close the backend and release any resources.
        This method is optional; backends may implement it as needed.
        """
        ...


__all__ = [
    "MemoryCapabilities",
    "MemoryBackend",
]