"""
===============================================================================
Hermes Capability Registry
===============================================================================
"""

from __future__ import annotations

from hermes.capability.capability import Capability
from hermes.capability.enums import CapabilityType


class CapabilityRegistry:

    def __init__(self) -> None:

        self._capabilities: dict[
            CapabilityType,
            Capability,
        ] = {}

    # -------------------------------------------------------------

    def register(
        self,
        capability: Capability,
    ) -> None:

        self._capabilities[capability.name] = capability

    # -------------------------------------------------------------

    def get(
        self,
        capability: CapabilityType,
    ) -> Capability | None:

        return self._capabilities.get(
            capability,
        )

    # -------------------------------------------------------------

    def all(
        self,
    ) -> list[Capability]:

        return list(self._capabilities.values())
