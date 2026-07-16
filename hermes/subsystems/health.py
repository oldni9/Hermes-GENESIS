"""
===============================================================================
Hermes Subsystem Health
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from hermes.subsystems.registry import SubsystemRegistry


@dataclass(slots=True)
class SubsystemHealth:

    healthy: bool

    total: int

    loaded: int


class SubsystemHealthChecker:

    def check(
        self,
        registry: SubsystemRegistry,
    ) -> SubsystemHealth:

        total = len(registry)

        loaded = len(registry.values())

        return SubsystemHealth(

            healthy=True,

            total=total,

            loaded=loaded,

        )