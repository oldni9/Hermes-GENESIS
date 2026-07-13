# hermes/runtime/context.py

"""
===============================================================================
Hermes Runtime Context

Shared runtime state for a single Hermes instance.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class RuntimeContext:
    """
    Shared application context.

    This object stores long-lived runtime resources
    that are shared across the Hermes instance.
    """

    started: bool = False

    values: dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------

    def set(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Store a runtime value.
        """

        self.values[key] = value

    # ------------------------------------------------------------------

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve a runtime value.
        """

        return self.values.get(key, default)

    # ------------------------------------------------------------------

    def remove(
        self,
        key: str,
    ) -> None:
        """
        Remove a runtime value.
        """

        self.values.pop(key, None)

    # ------------------------------------------------------------------

    def clear(
        self,
    ) -> None:
        """
        Reset runtime state.
        """

        self.values.clear()