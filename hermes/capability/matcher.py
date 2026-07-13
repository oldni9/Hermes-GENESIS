"""
===============================================================================
Hermes Capability Matcher
===============================================================================
"""

from __future__ import annotations

from hermes.capability.capability import Capability
from hermes.intelligence.plan import ExecutionPlan


class CapabilityMatcher:

    def match(
        self,
        plan: ExecutionPlan,
        capabilities: list[Capability],
    ) -> Capability | None:

        for capability in capabilities:

            if capability.name == plan.intent.name:

                return capability

        return None