"""
===============================================================================
Hermes Kernel Executor

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.kernel.kernel_task import KernelTask
from hermes.kernel.result import TaskResult

from hermes.providers.manager import ProviderManager
from hermes.providers.request import ProviderRequest

from hermes.capability.enums import CapabilityType


class KernelExecutor:

    def __init__(self) -> None:

        self.providers = ProviderManager()

    # ------------------------------------------------------------------

    def execute(
        self,
        task: KernelTask,
    ) -> TaskResult:

        try:

            request = ProviderRequest(

                prompt=str(
                    task.payload,
                ),

            )

            result = self.providers.execute(

                request,

                CapabilityType.CHAT,

            )

            return TaskResult(

                task_id=task.id,

                success=result.success,

                output=result.text,

                error=None,

            )

        except Exception as exc:

            return TaskResult(

                task_id=task.id,

                success=False,

                output=None,

                error=str(exc),

            )