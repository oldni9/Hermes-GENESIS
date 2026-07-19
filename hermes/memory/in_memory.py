"""
===============================================================================
Hermes In-Memory Memory Backend
===============================================================================
"""
from __future__ import annotations

import copy
import time
import uuid
from typing import List

from .backend import MemoryBackend, MemoryCapabilities
from .models import MemoryEntry
from .exceptions import MemoryError


class InMemoryBackend(MemoryBackend):
    """
    In-memory implementation of MemoryBackend.
    Stores entries in a list; does not persist.
    """

    def __init__(self) -> None:
        self._entries: List[MemoryEntry] = []

    @property
    def capabilities(self) -> MemoryCapabilities:
        return MemoryCapabilities(
            persistent=False,
            semantic_search=False,
            delete=True,
            metadata_filtering=False,
        )

    def add(self, entry: MemoryEntry) -> str:
        """Add a memory entry. The backend generates the ID and timestamp."""
        # Deep copy metadata to preserve true immutability
        new_entry = MemoryEntry(
            id=str(uuid.uuid4()),
            content=entry.content,
            tags=entry.tags,
            timestamp=time.time(),
            score=entry.score,
            metadata=copy.deepcopy(dict(entry.metadata)),
        )
        self._entries.append(new_entry)
        return new_entry.id

    def _search_impl(self, query: str, limit: int) -> list[MemoryEntry]:
        """Internal search implementation (isolated for future replacement)."""
        query_lower = query.lower()
        results = [
            entry for entry in self._entries
            if query_lower in entry.content.lower()
        ]
        results.sort(key=lambda e: (e.score, e.timestamp), reverse=True)
        return results[:limit]

    def search(self, query: str, limit: int = 10) -> list[MemoryEntry]:
        return self._search_impl(query, limit)

    def count(self) -> int:
        return len(self._entries)

    def delete(self, entry_id: str) -> bool:
        for i, entry in enumerate(self._entries):
            if entry.id == entry_id:
                del self._entries[i]
                return True
        return False

    def clear(self) -> None:
        self._entries.clear()

    def close(self) -> None:
        pass