"""
===============================================================================
Text Content
===============================================================================
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any

from .base import Content, ContentKind, MetadataType
from .validators import validate_data_string

@dataclass(frozen=True, slots=True)
class TextContent(Content):
    text: str
    metadata: MetadataType = field(default_factory=dict)

    def __post_init__(self) -> None:
        validate_data_string(self.text, "text")

    @property
    def kind(self) -> ContentKind:
        return ContentKind.TEXT

    def to_dict(self) -> Dict[str, Any]:
        return {
            "kind": self.kind.value,
            "text": self.text,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TextContent:
        return cls(
            text=data["text"],
            metadata=data.get("metadata", {}),
        )

    def __hash__(self) -> int:
        metadata_str = self._metadata_hash(self.metadata)
        return hash((self.kind, self.text, metadata_str))