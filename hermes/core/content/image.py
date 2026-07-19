"""
===============================================================================
Image Content
===============================================================================
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, Optional

from .base import Content, ContentKind, MetadataType
from .validators import validate_mime_type, validate_dimensions, validate_data_string

@dataclass(frozen=True, slots=True)
class ImageContent(Content):
    data: str
    mime_type: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    metadata: MetadataType = field(default_factory=dict)

    def __post_init__(self) -> None:
        validate_data_string(self.data, "data")
        validate_mime_type(self.mime_type)
        validate_dimensions(self.width, self.height)

    @property
    def kind(self) -> ContentKind:
        return ContentKind.IMAGE

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "kind": self.kind.value,
            "data": self.data,
            "metadata": self.metadata,
        }
        if self.mime_type is not None:
            result["mime_type"] = self.mime_type
        if self.width is not None:
            result["width"] = self.width
        if self.height is not None:
            result["height"] = self.height
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ImageContent:
        return cls(
            data=data["data"],
            mime_type=data.get("mime_type"),
            width=data.get("width"),
            height=data.get("height"),
            metadata=data.get("metadata", {}),
        )

    def __hash__(self) -> int:
        metadata_str = self._metadata_hash(self.metadata)
        return hash((self.kind, self.data, self.mime_type, self.width, self.height, metadata_str))