"""
===============================================================================
Hermes Kernel Manager

Coordinates execution of KernelTasks.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.execution.service import ExecutionService
from hermes.kernel.executor import KernelExecutor
from hermes.kernel.kernel_task_bundle import KernelTaskBundle
from hermes.kernel.result import TaskResult


class KernelManager:
    """
    Executes every KernelTask inside a KernelTaskBundle.
    """

    def __init__(self, execution: ExecutionService) -> None:
        self.executor = KernelExecutor(execution)

    # ------------------------------------------------------------------

    def execute(
        self,
        bundle: KernelTaskBundle,
    ) -> list[TaskResult]:
        """
        Execute every task inside the bundle.
        (Sequential execution for now.)
        """
        results: list[TaskResult] = []

        for task in bundle:
            result = self.executor.execute_task(task)
            results.append(
                TaskResult(
                    task_id=task.id,
                    success=result.success,
                    output=result.text,
                    error=result.error,
                )
            )

        return results