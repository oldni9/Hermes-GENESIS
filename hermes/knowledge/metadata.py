"""
===============================================================================
Hermes Knowledge Metadata

Metadata attached to every KnowledgeDocument.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class KnowledgeMetadata:
    """
    AI and system metadata describing a knowledge document.
    """

    language: str = ""

    summary: str = ""

    keywords: list[str] = field(
        default_factory=list,
    )

    categories: list[str] = field(
        default_factory=list,
    )

    people: list[str] = field(
        default_factory=list,
    )

    places: list[str] = field(
        default_factory=list,
    )

    objects: list[str] = field(
        default_factory=list,
    )

    ocr_complete: bool = False

    embedding_complete: bool = False

    image_tagged: bool = False

    metadata: dict = field(
        default_factory=dict,
    )
