"""
===============================================================================
Hermes Runtime Provider

Represents a configurable Provider.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class RuntimeProvider:
    """
    Runtime representation of a provider.

    Providers are configurable objects.

    They do NOT contain networking code.
    """

    name: str

    adapter: str

    enabled: bool = True

    priority: int = 100

    models: list[str] = field(default_factory=list)

    metadata: dict = field(default_factory=dict)