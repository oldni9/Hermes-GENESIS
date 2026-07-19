"""
===============================================================================
Hermes Service Metadata

Describes a Hermes service.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field


@dataclass(slots=True)
class ServiceMetadata:
    """
    Static information describing a service.
    """

    name: str

    version: str = "1.0"

    description: str = ""

    author: str = "Aryan"

    category: str = ""

    tags: list[str] = field(default_factory=list)

    dependencies: list[str] = field(default_factory=list)

    enabled: bool = True
