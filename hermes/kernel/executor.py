"""
===============================================================================
Hermes Kernel Executor

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.capability.enums import CapabilityType

from hermes.execution.service import ExecutionService

from hermes.providers.result import ProviderResult


class KernelExecutor:
    """
    Thin wrapper around ExecutionService.

    The Kernel owns no routing logic.
    The Kernel owns no providers.
    """

    def __init__(
        self,
        execution: ExecutionService,
    ) -> None:

        self.execution = execution

    # ------------------------------------------------------------------

    def execute(
        self,
        prompt: str,
        capability: CapabilityType = CapabilityType.CHAT,
    ) -> ProviderResult:

        return self.execution.execute(
            prompt,
            capability,
        )