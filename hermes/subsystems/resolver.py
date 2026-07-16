"""
===============================================================================
Hermes Subsystem Resolver
===============================================================================
"""

from __future__ import annotations

from hermes.subsystems.base import BaseSubsystem
from hermes.subsystems.registry import SubsystemRegistry


class SubsystemResolver:

    def __init__(
        self,
        registry: SubsystemRegistry,
    ) -> None:

        self.registry = registry

    # ---------------------------------------------------------

    def resolve(
        self,
        name: str,
    ) -> BaseSubsystem | None:

        return self.registry.get(name)