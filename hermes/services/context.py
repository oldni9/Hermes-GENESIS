"""
===============================================================================
Hermes Service Context

Runtime context shared by an individual service instance.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field


@dataclass(slots=True)
class ServiceContext:
    """
    Mutable runtime context for a service.

    Stores temporary runtime information without exposing
    internal implementation details.
    """

    workspace: str = ""

    session_id: str = ""

    provider: str = ""

    model: str = ""

    metadata: dict = field(default_factory=dict)

    # ------------------------------------------------------------------

    def set(
        self,
        key: str,
        value,
    ) -> None:

        self.metadata[key] = value

    # ------------------------------------------------------------------

    def get(
        self,
        key: str,
        default=None,
    ):

        return self.metadata.get(
            key,
            default,
        )

    # ------------------------------------------------------------------

    def remove(
        self,
        key: str,
    ) -> None:

        self.metadata.pop(
            key,
            None,
        )

    # ------------------------------------------------------------------

    def clear(self) -> None:

        self.metadata.clear()