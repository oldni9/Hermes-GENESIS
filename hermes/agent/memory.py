"""
===============================================================================
Hermes Agent Memory
===============================================================================
"""
from __future__ import annotations

from typing import Any, Dict, Optional, Sequence

from hermes.memory.backend import MemoryBackend, MemoryCapabilities
from hermes.memory.in_memory import InMemoryBackend
from hermes.memory.models import MemoryEntry


class AgentMemory:
    """
    Agent memory layer.
    Uses a MemoryBackend for storage.
    """

    def __init__(self, backend: Optional[MemoryBackend] = None) -> None:
        self._backend = backend or InMemoryBackend()

    @property
    def backend(self) -> MemoryBackend:
        """Return the underlying memory backend."""
        return self._backend

    def add(
        self,
        content: str,
        tags: Optional[Sequence[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Add a memory entry.
        Tags and metadata are stored as first-class fields.
        """
        entry = MemoryEntry(
            content=content,
            tags=tuple(tags) if tags is not None else (),
            metadata=metadata or {},
        )
        return self._backend.add(entry)

    def search(self, query: str, limit: int = 10) -> list[MemoryEntry]:
        return self._backend.search(query, limit)

    def delete(self, entry_id: str) -> bool:
        return self._backend.delete(entry_id)

    def clear(self) -> None:
        self._backend.clear()

    def count(self) -> int:
        return self._backend.count()

    def __len__(self) -> int:
        return self.count()

    def close(self) -> None:
        self._backend.close()