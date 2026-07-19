"""
===============================================================================
Hermes Capability
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from hermes.capability.enums import CapabilityType


@dataclass(slots=True)
class Capability:

    name: CapabilityType

    description: str = ""

    enabled: bool = True

    metadata: dict[str, Any] = field(default_factory=dict)
