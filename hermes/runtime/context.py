"""
===============================================================================
Hermes Runtime Context
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class RuntimeContext:
    """
    Shared runtime context.

    Temporary values that subsystems may read/write.
    """

    values: dict = field(
        default_factory=dict,
    )

    def set(self, key: str, value) -> None:
        self.values[key] = value

    def get(self, key: str, default=None):
        return self.values.get(key, default)

    def clear(self) -> None:
        self.values.clear()