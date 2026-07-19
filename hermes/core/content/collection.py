"""
===============================================================================
Content Collection
===============================================================================
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Iterator, Optional, Any, Dict

from .base import Content, ContentKind
from .text import TextContent
from .image import ImageContent
from .audio import AudioContent
from .video import VideoContent
from .file import FileContent
from .structured import StructuredContent

@dataclass(slots=True)
class ContentCollection:
    contents: List[Content] = field(default_factory=list)

    def add(self, content: Content) -> None:
        self.contents.append(content)

    def remove(self, content: Content) -> None:
        self.contents = [c for c in self.contents if c != content]

    def extend(self, items: List[Content]) -> None:
        self.contents.extend(items)

    def clear(self) -> None:
        self.contents.clear()

    def copy(self) -> ContentCollection:
        return ContentCollection(self.contents.copy())

    def __len__(self) -> int:
        return len(self.contents)

    def __iter__(self) -> Iterator[Content]:
        return iter(self.contents)

    def __getitem__(self, index: int) -> Content:
        return self.contents[index]

    def first(self) -> Optional[Content]:
        return self.contents[0] if self.contents else None

    def get(self, index: int) -> Optional[Content]:
        if 0 <= index < len(self.contents):
            return self.contents[index]
        return None

    def filter_by_kind(self, kind: ContentKind | str) -> ContentCollection:
        kind_val = kind.value if isinstance(kind, ContentKind) else kind
        return ContentCollection(
            [c for c in self.contents if c.kind.value == kind_val]
        )

    def texts(self) -> List[TextContent]:
        return [c for c in self.contents if isinstance(c, TextContent)]

    def images(self) -> List[ImageContent]:
        return [c for c in self.contents if isinstance(c, ImageContent)]

    def audio(self) -> List[AudioContent]:
        return [c for c in self.contents if isinstance(c, AudioContent)]

    def video(self) -> List[VideoContent]:
        return [c for c in self.contents if isinstance(c, VideoContent)]

    def files(self) -> List[FileContent]:
        return [c for c in self.contents if isinstance(c, FileContent)]

    def structured(self) -> List[StructuredContent]:
        return [c for c in self.contents if isinstance(c, StructuredContent)]

    def to_dict(self) -> List[Dict[str, Any]]:
        return [c.to_dict() for c in self.contents]

    @classmethod
    def from_dict(cls, data: List[Dict[str, Any]]) -> ContentCollection:
        from .factory import content_from_dict
        return cls([content_from_dict(item) for item in data])

    def __hash__(self) -> int:
        return hash(tuple(self.contents))