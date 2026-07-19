"""
===============================================================================
Hermes Knowledge Source

Represents where a KnowledgeDocument originated.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field

from datetime import datetime


@dataclass(slots=True)
class KnowledgeSource:
    """
    Origin of a knowledge document.
    """

    name: str = ""

    type: str = ""

    location: str = ""

    created_at: datetime = field(
        default_factory=datetime.utcnow,
    )

    metadata: dict = field(
        default_factory=dict,
    )

    def __str__(self):

        if self.location:

            return f"{self.type}:{self.location}"

        return self.type
