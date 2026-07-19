"""
===============================================================================
Video Content
===============================================================================
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, Optional

from .base import Content, ContentKind
from .validators import validate_data_string, validate_mime_type, validate_duration, validate_dimensions

@dataclass(frozen=True, slots=True)
class VideoContent(Content):
    data: str
    mime_type: Optional[str] = None
    duration: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None

    def __post_init__(self) -> None:
        validate_data_string(self.data, "data")
        validate_mime_type(self.mime_type)
        validate_duration(self.duration)
        validate_dimensions(self.width, self.height)

    @property
    def kind(self) -> ContentKind:
        return ContentKind.VIDEO

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "kind": self.kind.value,
            "data": self.data,
            "metadata": self.metadata,
        }
        if self.mime_type is not None:
            result["mime_type"] = self.mime_type
        if self.duration is not None:
            result["duration"] = self.duration
        if self.width is not None:
            result["width"] = self.width
        if self.height is not None:
            result["height"] = self.height
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> VideoContent:
        return cls(
            data=data["data"],
            mime_type=data.get("mime_type"),
            duration=data.get("duration"),
            width=data.get("width"),
            height=data.get("height"),
            metadata=data.get("metadata", {}),
        )