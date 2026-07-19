"""
===============================================================================
Tests for Hermes Content Abstractions
===============================================================================
"""
from __future__ import annotations

import pytest
from hermes.core.content import (
    ContentKind,
    TextContent,
    ImageContent,
    AudioContent,
    VideoContent,
    FileContent,
    FileSourceType,
    StructuredContent,
    ContentCollection,
    content_from_dict,
    register_content_type,
    JSONType,
)


class TestContent:
    def test_text_content_create(self):
        tc = TextContent(text="Hello world")
        assert tc.kind == ContentKind.TEXT
        assert tc.text == "Hello world"

    def test_text_content_validation(self):
        with pytest.raises(ValueError, match="must be a non-empty string"):
            TextContent(text="")
        with pytest.raises(ValueError, match="must be a non-empty string"):
            TextContent(text=123)  # type: ignore

    def test_text_content_serialization(self):
        tc = TextContent(text="Hello", metadata={"lang": "en"})
        d = tc.to_dict()
        assert d["kind"] == "text"
        assert d["text"] == "Hello"
        assert d["metadata"] == {"lang": "en"}
        tc2 = TextContent.from_dict(d)
        assert tc == tc2

    def test_text_content_hash(self):
        tc1 = TextContent(text="Hello", metadata={"lang": "en"})
        tc2 = TextContent(text="Hello", metadata={"lang": "en"})
        tc3 = TextContent(text="World", metadata={"lang": "en"})
        assert hash(tc1) == hash(tc2)
        assert hash(tc1) != hash(tc3)

    def test_image_content_create(self):
        ic = ImageContent(data="https://example.com/image.png", mime_type="image/png", width=100, height=200)
        assert ic.kind == ContentKind.IMAGE
        assert ic.data == "https://example.com/image.png"
        assert ic.mime_type == "image/png"
        assert ic.width == 100
        assert ic.height == 200

    def test_image_content_validation(self):
        with pytest.raises(ValueError, match="non-empty string"):
            ImageContent(data="")
        with pytest.raises(TypeError):
            ImageContent(data="x", width="100")  # type: ignore
        with pytest.raises(ValueError, match="MIME"):
            ImageContent(data="x", mime_type="invalid")

    def test_image_content_serialization(self):
        ic = ImageContent(data="data:image/png;base64,xyz", mime_type="image/png")
        d = ic.to_dict()
        assert d["kind"] == "image"
        assert d["data"] == "data:image/png;base64,xyz"
        assert d["mime_type"] == "image/png"
        ic2 = ImageContent.from_dict(d)
        assert ic == ic2

    def test_audio_content_create(self):
        ac = AudioContent(data="audio.mp3", duration=30.5)
        assert ac.kind == ContentKind.AUDIO
        assert ac.duration == 30.5

    def test_audio_content_validation(self):
        with pytest.raises(ValueError, match="non-empty string"):
            AudioContent(data="")
        with pytest.raises(TypeError):
            AudioContent(data="x", duration="30")  # type: ignore

    def test_video_content_create(self):
        vc = VideoContent(data="video.mp4", width=1920, height=1080)
        assert vc.kind == ContentKind.VIDEO
        assert vc.width == 1920
        assert vc.height == 1080

    def test_file_content_create(self):
        fc = FileContent(data=b"binary data", source_type=FileSourceType.BYTES, filename="file.bin", size=11)
        assert fc.kind == ContentKind.FILE
        assert fc.data == b"binary data"
        assert fc.source_type == FileSourceType.BYTES
        assert fc.filename == "file.bin"
        assert fc.size == 11

        fc2 = FileContent(data="/path/to/file.txt", source_type=FileSourceType.PATH, filename="file.txt")
        assert fc2.data == "/path/to/file.txt"
        assert fc2.source_type == FileSourceType.PATH

    def test_file_content_validation(self):
        with pytest.raises(ValueError, match="data cannot be None"):
            FileContent(data=None, source_type=FileSourceType.BYTES)  # type: ignore
        with pytest.raises(ValueError, match="source_type must be BYTES"):
            FileContent(data=b"bytes", source_type=FileSourceType.PATH)

    def test_file_content_serialization_bytes(self):
        fc = FileContent(data=b"\x00\x01\x02", source_type=FileSourceType.BYTES, filename="bin.bin")
        d = fc.to_dict()
        assert d["data"] == "000102"
        assert d["source_type"] == "bytes"
        assert d["encoding"] == "hex"
        fc2 = FileContent.from_dict(d)
        assert fc2.data == b"\x00\x01\x02"
        assert fc2.filename == "bin.bin"
        assert fc2.source_type == FileSourceType.BYTES

    def test_file_content_serialization_path(self):
        fc = FileContent(data="/path/to/file", source_type=FileSourceType.PATH)
        d = fc.to_dict()
        assert d["data"] == "/path/to/file"
        assert d["source_type"] == "path"
        fc2 = FileContent.from_dict(d)
        assert fc2.data == "/path/to/file"
        assert fc2.source_type == FileSourceType.PATH

    def test_structured_content_create(self):
        sc = StructuredContent(data={"key": "value", "list": [1, 2]})
        assert sc.kind == ContentKind.STRUCTURED
        assert sc.data == {"key": "value", "list": [1, 2]}

    def test_structured_content_serialization(self):
        sc = StructuredContent(data={"a": 1}, schema={"type": "object"})
        d = sc.to_dict()
        assert d["data"] == {"a": 1}
        assert d["schema"] == {"type": "object"}
        sc2 = StructuredContent.from_dict(d)
        assert sc == sc2

    def test_content_factory(self):
        data = {"kind": "text", "text": "test"}
        c = content_from_dict(data)
        assert isinstance(c, TextContent)
        assert c.text == "test"

        data = {"kind": "image", "data": "img.jpg"}
        c = content_from_dict(data)
        assert isinstance(c, ImageContent)

        with pytest.raises(ValueError, match="Unknown Content kind"):
            content_from_dict({"kind": "unknown"})

    def test_register_custom_content(self):
        from hermes.core.content.base import Content, ContentKind, MetadataType
        from dataclasses import dataclass, field

        @dataclass(frozen=True, slots=True)
        class CustomContent(Content):
            value: str
            metadata: MetadataType = field(default_factory=dict)

            @property
            def kind(self) -> ContentKind:
                return ContentKind.TEXT

            def to_dict(self) -> dict:
                return {"kind": self.kind.value, "value": self.value, "metadata": self.metadata}

            @classmethod
            def from_dict(cls, data: dict) -> CustomContent:
                return cls(value=data["value"], metadata=data.get("metadata", {}))

        register_content_type("custom", CustomContent)
        data = {"kind": "custom", "value": "test"}
        c = content_from_dict(data)
        assert isinstance(c, CustomContent)
        assert c.value == "test"

        # Overwrite protection
        with pytest.raises(ValueError, match="already registered"):
            register_content_type("text", CustomContent)


class TestContentCollection:
    def test_collection_operations(self):
        col = ContentCollection()
        tc = TextContent(text="hello")
        ic = ImageContent(data="img.jpg")
        col.add(tc)
        col.add(ic)
        assert len(col) == 2
        assert col.first() == tc
        assert col.get(0) == tc
        assert col.get(2) is None

        col2 = col.copy()
        assert len(col2) == 2
        col2.remove(tc)
        assert len(col2) == 1
        assert tc not in col2.contents

        col3 = col.filter_by_kind(ContentKind.TEXT)
        assert len(col3) == 1
        assert col3.contents[0] == tc

        texts = col.texts()
        assert len(texts) == 1
        assert texts[0] == tc

    def test_collection_serialization(self):
        col = ContentCollection([
            TextContent(text="a"),
            ImageContent(data="b"),
        ])
        d = col.to_dict()
        assert len(d) == 2
        col2 = ContentCollection.from_dict(d)
        assert len(col2) == 2
        assert col2.contents[0].text == "a"
        assert col2.contents[1].data == "b"


class TestJSONType:
    def test_recursive_json_type(self):
        from hermes.core.content.structured import JSONType
        data: JSONType = {"a": 1, "b": [2, {"c": 3}]}
        sc = StructuredContent(data=data)
        assert sc.data == data