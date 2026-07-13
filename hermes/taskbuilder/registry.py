"""
===============================================================================
Hermes Task Builder Registry

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.kernel.kernel_task import KernelTask


class TaskBuilderRegistry:
    """
    Stores built tasks.
    """

    def __init__(self) -> None:

        self._tasks: list[Task] = []

    # ------------------------------------------------------------------

    def add(
        self,
        task: Task,
    ) -> None:

        self._tasks.append(task)

    # ------------------------------------------------------------------

    def all(
        self,
    ) -> list[Task]:

        return list(self._tasks)

    # ------------------------------------------------------------------

    def clear(
        self,
    ) -> None:

        self._tasks.clear()