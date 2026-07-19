"""
===============================================================================
Structured Content
===============================================================================
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Union, List

from .base import Content, ContentKind, MetadataType

JSONPrimitive = Union[str, int, float, bool, None]
JSONType = Union[JSONPrimitive, List["JSONType"], Dict[str, "JSONType"]]

@dataclass(frozen=True, slots=True)
class StructuredContent(Content):
    data: JSONType
    schema: Optional[JSONType] = None
    metadata: MetadataType = field(default_factory=dict)

    @property
    def kind(self) -> ContentKind:
        return ContentKind.STRUCTURED

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "kind": self.kind.value,
            "data": self.data,
            "metadata": self.metadata,
        }
        if self.schema is not None:
            result["schema"] = self.schema
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> StructuredContent:
        return cls(
            data=data["data"],
            schema=data.get("schema"),
            metadata=data.get("metadata", {}),
        )

    def __hash__(self) -> int:
        metadata_str = self._metadata_hash(self.metadata)
        data_hash = json.dumps(self.data, sort_keys=True, default=str)
        schema_hash = json.dumps(self.schema, sort_keys=True, default=str) if self.schema is not None else ""
        return hash((self.kind, data_hash, schema_hash, metadata_str))