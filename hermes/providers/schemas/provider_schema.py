"""
===============================================================================
Hermes Provider Schema

Internal immutable representation of a provider loaded from YAML.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ProviderInfo:
    """
    Canonical provider description.

    Registry stores only ProviderInfo objects.
    """

    name: str

    provider_type: str

    enabled: bool = True

    priority: int = 100

    api_base: str = ""

    default_model: str = ""

    models: list[str] = field(default_factory=list)

    capabilities: list[str] = field(default_factory=list)

    metadata: dict = field(default_factory=dict)
