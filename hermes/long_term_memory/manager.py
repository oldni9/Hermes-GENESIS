"""
===============================================================================
Memory Manager
===============================================================================

Dependencies:
    - hermes.long_term_memory.store
    - hermes.long_term_memory.models

Consumes:
    - MemoryStore

Produces:
    - MemoryManager

Public API:
    - MemoryManager

TODO:
    - Replace ValueError with typed exceptions (MemoryNotFoundError, MemoryValidationError).
    - Add memory scoring and ranking algorithms.
    - Add memory compression/summarization.
===============================================================================
"""

from __future__ import annotations

from typing import List, Optional

from hermes.long_term_memory.models import MemoryRecord
from hermes.long_term_memory.store import MemoryStore


class MemoryManager:
    """
    Thin wrapper over MemoryStore.
    Responsible for validation and future persistence.
    """

    def __init__(self, store: Optional[MemoryStore] = None) -> None:
        self._store = store or MemoryStore()

    def add(self, content: str, metadata: Optional[dict] = None) -> MemoryRecord:
        """Validate and add a new memory."""
        if not isinstance(content, str) or not content.strip():
            raise ValueError("Memory content cannot be empty.")
        return self._store.add(content, metadata)

    def update(
        self, 
        record_id: str, 
        content: Optional[str] = None, 
        metadata: Optional[dict] = None
    ) -> Optional[MemoryRecord]:
        """Update an existing memory."""
        return self._store.update(record_id, content, metadata)

    def delete(self, record_id: str) -> bool:
        """Delete a memory."""
        return self._store.delete(record_id)

    def clear(self) -> None:
        """Clear all memories."""
        self._store.clear()

    def get(self, record_id: str) -> Optional[MemoryRecord]:
        """Get a specific memory."""
        return self._store.get(record_id)

    def list(self) -> List[MemoryRecord]:
        """List all memories."""
        return self._store.list()

    def search(self, query: str) -> List[MemoryRecord]:
        """Search memories."""
        if not isinstance(query, str):
            raise ValueError("Search query must be a string.")
        return self._store.search(query)