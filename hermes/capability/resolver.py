"""
===============================================================================
Hermes Capability Resolver
===============================================================================
"""

from __future__ import annotations

from hermes.capability.matcher import CapabilityMatcher
from hermes.capability.registry import CapabilityRegistry
from hermes.intelligence.plan import ExecutionPlan


class CapabilityResolver:

    def __init__(
        self,
        registry: CapabilityRegistry,
    ) -> None:

        self._registry = registry

        self._matcher = CapabilityMatcher()

    def resolve(
        self,
        plan: ExecutionPlan,
    ):

        return self._matcher.match(
            plan,
            self._registry.all(),
        )