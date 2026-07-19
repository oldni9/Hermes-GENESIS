"""
===============================================================================
Planning → Execution Adapter
===============================================================================
"""
from __future__ import annotations

from typing import Optional

from hermes.execution.service import ExecutionService
from hermes.providers.result import ProviderResult
from hermes.planning.plan import Plan
from hermes.planning.domain import Domain
from hermes.planning.exceptions import PlanningError
from hermes.capability.enums import CapabilityType


class PlanExecutor:
    """
    Executes a Plan using the ExecutionService.

    For each PlanStep, the step's domain is resolved to a CapabilityType,
    and the step's instruction is passed to ExecutionService.execute().
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
        execution_service: ExecutionService,
        mapping: Optional[dict[Domain, CapabilityType | None]] = None,
    ) -> None:
        """
        Initialise the executor.

        Args:
            execution_service: The execution service to use.
            mapping: Optional custom mapping from Domain to CapabilityType.
                If a domain is mapped to None, the mapping is removed.
                Merges with defaults.
        """
        self._execution_service = execution_service
        self._mapping = self._DEFAULT_MAPPING.copy()
        if mapping:
            for domain, cap_type in mapping.items():
                if cap_type is None:
                    self._mapping.pop(domain, None)
                else:
                    self._mapping[domain] = cap_type

    def execute(self, plan: Plan) -> list[ProviderResult]:
        """
        Execute a Plan.
        Returns a list of ProviderResult objects, one per step.

        Raises:
            PlanningError: If a domain cannot be resolved,
                or if ExecutionService returns an error.
        """
        if not plan.steps:
            raise PlanningError("Cannot execute an empty Plan")

        results: list[ProviderResult] = []

        for step in plan.steps:
            # Resolve capability type
            cap_type = self._mapping.get(step.domain)
            if cap_type is None:
                raise PlanningError(f"No CapabilityType mapping for domain {step.domain.value}")

            # Execute step
            result = self._execution_service.execute(
                prompt=step.instruction,
                capability=cap_type,
            )

            if not result.success:
                raise PlanningError(
                    f"Execution failed for step '{step.instruction}': {result.error}"
                )

            results.append(result)

        return results