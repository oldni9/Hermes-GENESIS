"""
===============================================================================
Hermes Content Base
===============================================================================
"""
from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional, Mapping

# Type alias for metadata
MetadataType = Mapping[str, Any]

class ContentKind(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    FILE = "file"
    STRUCTURED = "structured"

@dataclass(frozen=True, slots=True)
class Content(ABC):
    """
    Abstract base for all Hermes content.
    Subclasses must define their own fields.
    """
    @property
    @abstractmethod
    def kind(self) -> ContentKind:
        """Return the content kind."""
        ...

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to a dictionary."""
        ...

    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> Content:
        """Deserialize from a dictionary."""
        ...

    def _metadata_hash(self, metadata: MetadataType) -> str:
        """Stable JSON representation of metadata."""
        def normalize(obj: Any) -> Any:
            if isinstance(obj, dict):
                return {str(k): normalize(v) for k, v in obj.items()}
            if isinstance(obj, (list, tuple)):
                return [normalize(v) for v in obj]
            if isinstance(obj, set):
                return [normalize(v) for v in sorted(obj)]
            if hasattr(obj, "__dict__"):
                return normalize(obj.__dict__)
            return obj

        normalized = normalize(metadata)
        return json.dumps(normalized, sort_keys=True, default=str)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Content):
            return NotImplemented
        return self.kind == other.kind and self.metadata == other.metadata

__all__ = [
    "Content",
    "ContentKind",
    "MetadataType",
]