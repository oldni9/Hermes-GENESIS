"""
===============================================================================
Content Factory – registry-based deserialization
===============================================================================
"""
from __future__ import annotations

from typing import Dict, Any, Type
import threading

from .base import Content, ContentKind
from .text import TextContent
from .image import ImageContent
from .audio import AudioContent
from .video import VideoContent
from .file import FileContent
from .structured import StructuredContent

_CONTENT_REGISTRY: Dict[str, Type[Content]] = {}
_REGISTRY_LOCK = threading.Lock()

def register_content_type(kind: str, cls: Type[Content], overwrite: bool = False) -> None:
    with _REGISTRY_LOCK:
        if not overwrite and kind in _CONTENT_REGISTRY:
            raise ValueError(f"Content kind '{kind}' is already registered")
        _CONTENT_REGISTRY[kind] = cls

register_content_type(ContentKind.TEXT.value, TextContent)
register_content_type(ContentKind.IMAGE.value, ImageContent)
register_content_type(ContentKind.AUDIO.value, AudioContent)
register_content_type(ContentKind.VIDEO.value, VideoContent)
register_content_type(ContentKind.FILE.value, FileContent)
register_content_type(ContentKind.STRUCTURED.value, StructuredContent)

def content_from_dict(data: Dict[str, Any]) -> Content:
    kind = data.get("kind")
    if not kind:
        raise ValueError("Missing 'kind' in content data")
    cls = _CONTENT_REGISTRY.get(kind)
    if cls is None:
        raise ValueError(f"Unknown Content kind: {kind}")
    return cls.from_dict(data)