"""
===============================================================================
Hermes Subsystem Metadata
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field


@dataclass(slots=True)
class SubsystemMetadata:

    name: str

    version: str = "1.0"

    description: str = ""

    author: str = "Aryan"

    commands: list[str] = field(
        default_factory=list,
    )