"""
===============================================================================
Hermes Runtime Policy

Represents a runtime execution policy.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class RuntimePolicy:
    """
    Runtime execution policy.
    """

    name: str

    enabled: bool = True

    priority: int = 100

    rules: dict = field(default_factory=dict)

    metadata: dict = field(default_factory=dict)
