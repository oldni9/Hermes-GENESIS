"""
===============================================================================
Hermes Model
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Model:

    name: str

    provider: str

    priority: int = 100

    enabled: bool = True

    metadata: dict[str, Any] = field(default_factory=dict)
