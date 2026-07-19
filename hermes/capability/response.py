"""
===============================================================================
Capability Response
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class CapabilityResponse:

    success: bool

    result: Any = None

    error: str | None = None

    metadata: dict[str, Any] = field(default_factory=dict)
