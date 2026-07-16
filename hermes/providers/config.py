"""
===============================================================================
Hermes Provider Configuration

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any


@dataclass(slots=True)
class ProviderConfig:
    """
    Unified provider configuration.

    Every provider client receives one ProviderConfig.
    """

    name: str

    api_key: str = ""

    base_url: str = ""

    default_model: str = ""

    organization: str = ""

    timeout: float = 60.0

    enabled: bool = True

    headers: dict[str, str] = field(default_factory=dict)

    options: dict[str, Any] = field(default_factory=dict)