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
from hermes.kernel.kernel_task import KernelTask
from hermes.providers.result import ProviderResult


class KernelExecutor:
    """
    Executes KernelTasks via the ExecutionService.
    """

    def __init__(
        self,
        execution: ExecutionService,
    ) -> None:

        self.execution = execution

    # ------------------------------------------------------------------

    def execute_task(
        self,
        task: KernelTask,
    ) -> ProviderResult:
        """
        Execute a KernelTask.
        Extracts the prompt and capability from the task's payload.
        """
        payload = task.payload or {}
        prompt = payload.get("prompt", "")
        if not prompt:
            prompt = payload.get("instruction", task.name)  # fallback
        capability = payload.get("capability", CapabilityType.CHAT)

        return self.execution.execute(
            prompt=prompt,
            capability=capability,
        )

    # ------------------------------------------------------------------

    def execute_prompt(
        self,
        prompt: str,
        capability: CapabilityType = CapabilityType.CHAT,
    ) -> ProviderResult:
        """
        Execute a simple prompt (backward compatibility).
        """
        return self.execution.execute(
            prompt=prompt,
            capability=capability,
        )