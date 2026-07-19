"""
===============================================================================
Hermes Runtime Profile

Represents a complete Hermes operating profile.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class RuntimeProfile:
    """
    Runtime operating profile.

    A profile bundles together all runtime
    objects required for one operating mode.
    """

    name: str

    enabled: bool = True

    default_pipeline: str = "default"

    default_policy: str = "default"

    default_scheduler: str = "default"

    providers: list[str] = field(default_factory=list)

    models: list[str] = field(default_factory=list)

    metadata: dict = field(default_factory=dict)
