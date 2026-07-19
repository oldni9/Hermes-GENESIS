"""
===============================================================================
File Content
===============================================================================
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Union
from enum import Enum

from .base import Content, ContentKind, MetadataType
from .validators import validate_mime_type, validate_file_data, validate_file_source_type

class FileSourceType(str, Enum):
    PATH = "path"
    URL = "url"
    BASE64 = "base64"
    BYTES = "bytes"

@dataclass(frozen=True, slots=True)
class FileContent(Content):
    data: Union[str, bytes]
    source_type: FileSourceType
    mime_type: Optional[str] = None
    filename: Optional[str] = None
    size: Optional[int] = None
    encoding: Optional[str] = None
    metadata: MetadataType = field(default_factory=dict)

    def __post_init__(self) -> None:
        validate_file_data(self.data)
        validate_file_source_type(self.source_type)
        validate_mime_type(self.mime_type)
        if self.encoding is not None and not isinstance(self.encoding, str):
            raise TypeError("encoding must be a string or None")
        if self.size is not None and not isinstance(self.size, int):
            raise TypeError("size must be an int or None")
        if self.filename is not None and not isinstance(self.filename, str):
            raise TypeError("filename must be a string or None")
        # Validate consistency
        if isinstance(self.data, bytes) and self.source_type != FileSourceType.BYTES:
            raise ValueError("If data is bytes, source_type must be BYTES")
        if self.source_type == FileSourceType.BYTES and not isinstance(self.data, bytes):
            raise ValueError("If source_type is BYTES, data must be bytes")
        if self.source_type == FileSourceType.PATH and not isinstance(self.data, str):
            raise ValueError("If source_type is PATH, data must be a string")
        if self.source_type == FileSourceType.URL and not isinstance(self.data, str):
            raise ValueError("If source_type is URL, data must be a string")
        if self.source_type == FileSourceType.BASE64 and not isinstance(self.data, str):
            raise ValueError("If source_type is BASE64, data must be a string")

    @property
    def kind(self) -> ContentKind:
        return ContentKind.FILE

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "kind": self.kind.value,
            "source_type": self.source_type.value,
            "metadata": self.metadata,
        }
        if self.source_type == FileSourceType.BYTES:
            result["data"] = self.data.hex()
            result["encoding"] = "hex"
        else:
            result["data"] = self.data
        if self.mime_type is not None:
            result["mime_type"] = self.mime_type
        if self.filename is not None:
            result["filename"] = self.filename
        if self.size is not None:
            result["size"] = self.size
        if self.encoding is not None and self.encoding != "hex":
            result["encoding"] = self.encoding
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> FileContent:
        source_type = FileSourceType(data.get("source_type", "bytes"))
        data_field = data["data"]
        encoding = data.get("encoding")
        if source_type == FileSourceType.BYTES:
            if encoding == "hex":
                data_field = bytes.fromhex(data_field)
            else:
                if isinstance(data_field, str):
                    data_field = data_field.encode("utf-8")
        return cls(
            data=data_field,
            source_type=source_type,
            mime_type=data.get("mime_type"),
            filename=data.get("filename"),
            size=data.get("size"),
            encoding=encoding,
            metadata=data.get("metadata", {}),
        )

    def __hash__(self) -> int:
        metadata_str = self._metadata_hash(self.metadata)
        data_hash = self.data if isinstance(self.data, str) else self.data.hex()
        return hash((self.kind, data_hash, self.source_type, self.mime_type, self.filename, self.size, metadata_str))