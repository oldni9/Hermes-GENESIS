"""
===============================================================================
Capability Context
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class CapabilityContext:

    values: dict[str, Any] = field(default_factory=dict)

    def set(
        self,
        key: str,
        value: Any,
    ) -> None:

        self.values[key] = value

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        return self.values.get(key, default)