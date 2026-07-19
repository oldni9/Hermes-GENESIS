"""
===============================================================================
Hermes Provider
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from hermes.capability.enums import CapabilityType
from hermes.providers.enums import ProviderType


@dataclass(slots=True)
class Provider:

    name: ProviderType

    capabilities: set[CapabilityType]

    enabled: bool = True

    metadata: dict[str, Any] = field(default_factory=dict)
