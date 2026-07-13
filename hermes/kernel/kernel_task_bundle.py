"""
===============================================================================
Hermes Kernel Task Bundle

Container for KernelTasks.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field

from hermes.kernel.kernel_task import KernelTask


@dataclass(slots=True)
class KernelTaskBundle:
    """
    Collection of KernelTasks produced from
    one ExecutionGraph.
    """

    tasks: list[KernelTask] = field(default_factory=list)

    # ------------------------------------------------------------------

    def add(
        self,
        task: KernelTask,
    ) -> None:

        self.tasks.append(task)

    # ------------------------------------------------------------------

    def __len__(
        self,
    ) -> int:

        return len(self.tasks)

    # ------------------------------------------------------------------

    def __iter__(
        self,
    ):

        return iter(self.tasks)