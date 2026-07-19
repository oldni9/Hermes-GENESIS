"""
===============================================================================
Semantic Memory Models
===============================================================================
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Optional, Tuple


@dataclass(slots=True, frozen=True)
class Document:
    """
    Immutable document model for semantic memory.
    """
    id: str
    text: str
    metadata: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    embedding: Optional[Tuple[float, ...]] = None
    created_at: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        # Ensure metadata is truly immutable
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))
        # Ensure embedding is a tuple if it's a list
        if self.embedding is not None and not isinstance(self.embedding, tuple):
            object.__setattr__(self, "embedding", tuple(self.embedding))

    def to_dict(self) -> dict[str, Any]:
        """Convert Document to a dictionary."""
        return {
            "id": self.id,
            "text": self.text,
            "metadata": dict(self.metadata),
            "embedding": list(self.embedding) if self.embedding else None,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Document:
        """Create Document from a dictionary."""
        return cls(
            id=data["id"],
            text=data["text"],
            metadata=data.get("metadata", {}),
            embedding=tuple(data["embedding"]) if data.get("embedding") else None,
            created_at=data.get("created_at", time.time()),
        )


@dataclass(slots=True, frozen=True)
class SearchResult:
    """
    Result of a search operation.
    Contains the document and its similarity score.
    """
    document: Document
    score: float