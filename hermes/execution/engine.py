"""
===============================================================================
Hermes Execution Engine

Executes a KernelTaskBundle through the Kernel.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.execution.result import ExecutionResult

from hermes.kernel import (
    KernelManager,
    KernelTaskBundle,
)


class ExecutionEngine:
    """
    Executes a KernelTaskBundle.

        KernelTaskBundle
                ↓
          KernelManager
                ↓
          KernelExecutor
                ↓
         list[TaskResult]
                ↓
      list[ExecutionResult]
    """

    def __init__(self) -> None:

        self.kernel = KernelManager()

    # ------------------------------------------------------------------

    def execute(
        self,
        bundle: KernelTaskBundle,
    ) -> list[ExecutionResult]:

        task_results = self.kernel.execute(
            bundle,
        )

        results: list[ExecutionResult] = []

        for result in task_results:

            results.append(
                ExecutionResult(
                    success=result.success,
                    output=result.output,
                    error=result.error,
                )
            )

        return results
