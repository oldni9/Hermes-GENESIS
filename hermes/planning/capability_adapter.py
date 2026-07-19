"""
===============================================================================
Planning → Capability Adapter
===============================================================================
"""
from __future__ import annotations

from typing import Optional

from hermes.capability.manager import CapabilityManager
from hermes.capability.resolver import CapabilityResolver
from hermes.capability.enums import CapabilityType
from hermes.capability.capability import Capability
from hermes.intelligence.plan import ExecutionPlan
from hermes.intelligence.intent import Intent
from hermes.planning.plan import Plan
from hermes.planning.domain import Domain
from hermes.planning.exceptions import PlanningError


class PlanToExecutionPlanAdapter:
    """
    Adapter that converts a Planning Plan into an ExecutionPlan
    and resolves it using the existing CapabilityResolver.

    Currently only the first PlanStep is used for capability resolution.
    Multi-step plans will be supported in a future PR.
    """

    # Default mapping from Domain to CapabilityType
    _DEFAULT_MAPPING = {
        Domain.GENERAL: CapabilityType.CHAT,
        Domain.CHAT: CapabilityType.CHAT,
        Domain.CODE: CapabilityType.CODE,
        Domain.REASONING: CapabilityType.REASONING,
        Domain.SEARCH: CapabilityType.WEB,
        Domain.SUMMARIZE: CapabilityType.CHAT,
        Domain.TRANSLATE: CapabilityType.CHAT,
    }

    def __init__(
        self,
        resolver: Optional[CapabilityResolver] = None,
        mapping: Optional[dict[Domain, CapabilityType | None]] = None,
    ) -> None:
        """
        Initialise the adapter.

        Args:
            resolver: An existing CapabilityResolver instance. If None, a default
                one is created using CapabilityManager.
            mapping: Optional custom mapping from Domain to CapabilityType.
                If a domain is mapped to None, the mapping is removed.
                Merges with defaults.
        """
        if resolver is None:
            manager = CapabilityManager()
            # manager.registry is a public attribute
            self._resolver = CapabilityResolver(manager.registry)
        else:
            self._resolver = resolver

        self._mapping = self._DEFAULT_MAPPING.copy()
        if mapping:
            for domain, cap_type in mapping.items():
                if cap_type is None:
                    self._mapping.pop(domain, None)
                else:
                    self._mapping[domain] = cap_type

    def resolve(self, plan: Plan) -> Capability:
        """
        Convert a Plan to an ExecutionPlan and resolve it to a Capability.
        Only the first PlanStep is used for resolution.

        Raises:
            PlanningError: If the plan is empty, the domain cannot be mapped,
                or the resolver returns None.
        """
        if not plan.steps:
            raise PlanningError("Cannot resolve an empty Plan")

        # Use the first step's domain to determine the CapabilityType
        first_step = plan.steps[0]
        cap_type = self._mapping.get(first_step.domain)
        if cap_type is None:
            raise PlanningError(f"No CapabilityType mapping for domain {first_step.domain.value}")

        # Build an ExecutionPlan with the intent name set to the capability type's value
        intent = Intent(name=cap_type.value, confidence=1.0)
        steps = [step.instruction for step in plan.steps]
        execution_plan = ExecutionPlan(
            intent=intent,
            steps=steps,
            metadata=plan.metadata.copy(),
        )

        # Resolve using the existing CapabilityResolver
        capability = self._resolver.resolve(execution_plan)
        if capability is None:
            raise PlanningError(f"No capability resolved for intent '{cap_type.value}'")

        return capability