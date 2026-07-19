"""
===============================================================================
Audio Content
===============================================================================
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, Optional

from .base import Content, ContentKind
from .validators import validate_data_string, validate_mime_type, validate_duration

@dataclass(frozen=True, slots=True)
class AudioContent(Content):
    data: str
    mime_type: Optional[str] = None
    duration: Optional[float] = None

    def __post_init__(self) -> None:
        validate_data_string(self.data, "data")
        validate_mime_type(self.mime_type)
        validate_duration(self.duration)

    @property
    def kind(self) -> ContentKind:
        return ContentKind.AUDIO

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
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AudioContent:
        return cls(
            data=data["data"],
            mime_type=data.get("mime_type"),
            duration=data.get("duration"),
            metadata=data.get("metadata", {}),
        )