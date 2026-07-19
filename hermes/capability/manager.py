"""
===============================================================================
Hermes Capability Manager
===============================================================================
"""

from __future__ import annotations

from hermes.capability.capability import Capability
from hermes.capability.enums import CapabilityType
from hermes.capability.registry import CapabilityRegistry


class CapabilityManager:

    def __init__(self) -> None:

        self.registry = CapabilityRegistry()

        self._bootstrap()

    # -------------------------------------------------------------

    def _bootstrap(
        self,
    ) -> None:

        for capability in CapabilityType:

            self.registry.register(
                Capability(
                    name=capability,
                )
            )

    # -------------------------------------------------------------

    def get(
        self,
        capability: CapabilityType,
    ) -> Capability | None:

        return self.registry.get(
            capability,
        )
