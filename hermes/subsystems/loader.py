"""
===============================================================================
Hermes Subsystem Loader
===============================================================================
"""

from __future__ import annotations

from hermes.subsystems.base import BaseSubsystem
from hermes.subsystems.registry import SubsystemRegistry


class SubsystemLoader:

    def __init__(
        self,
        registry: SubsystemRegistry,
    ) -> None:

        self.registry = registry

    def load(
        self,
        subsystem: BaseSubsystem,
    ):

        self.registry.register(subsystem)

        return subsystem
