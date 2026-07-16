"""
===============================================================================
Hermes Knowledge Document

Universal knowledge object.

Everything Hermes knows becomes a KnowledgeDocument.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field

from datetime import datetime

import uuid


@dataclass(slots=True)
class KnowledgeDocument:
    """
    Universal Hermes knowledge object.
    """

    id: str = field(

        default_factory=lambda: uuid.uuid4().hex,

    )

    title: str = ""

    content: str = ""

    source: str = ""

    type: str = ""

    language: str = ""

    created_at: datetime = field(

        default_factory=datetime.utcnow,

    )

    updated_at: datetime = field(

        default_factory=datetime.utcnow,

    )

    tags: list[str] = field(

        default_factory=list,

    )

    metadata: dict = field(

        default_factory=dict,

    )

    embedding_id: str = ""

    checksum: str = ""

    indexed: bool = False

    def touch(self):

        self.updated_at = datetime.utcnow()