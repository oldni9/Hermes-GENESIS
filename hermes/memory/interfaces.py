"""
===============================================================================
Hermes Memory Interfaces
===============================================================================

Sprint 13 Update:
Introduced EpisodicStore and SemanticStore protocols to decouple
UnifiedMemoryManager from concrete backend implementations.
===============================================================================
"""
from __future__ import annotations

from typing import Protocol, runtime_checkable, List, Optional
from hermes.memory.models import MemoryEntry


@runtime_checkable
class EpisodicStore(Protocol):
    """Protocol for episodic memory backends."""
    def add(self, entry: MemoryEntry) -> str: ...
    def search(self, query: str, limit: int = 10) -> List[MemoryEntry]: ...
    def count(self) -> int: ...
    def delete(self, entry_id: str) -> bool: ...
    def clear(self) -> None: ...
    def close(self) -> None: ...


@runtime_checkable
class SemanticStore(Protocol):
    """Protocol for semantic memory backends."""
    def remember(self, text: str, metadata: Optional[dict] = None) -> str: ...
    def search(self, query: str, top_k: int = 10) -> List: ... # Returns list of Document-like objects
    def delete(self, document_id: str) -> None: ...
    def clear(self) -> None: ...
    def count(self) -> int: ...