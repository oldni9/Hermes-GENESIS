"""
===============================================================================
Hermes Task Builder

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.kernel.kernel_task import KernelTask
from hermes.taskbuilder.context import TaskBuilderContext


class TaskBuilder:
    """
    Builds KernelTasks from TaskBuilderContext.
    """

    def build(
        self,
        context: TaskBuilderContext,
    ) -> KernelTask:
        """
        Convert a TaskBuilderContext into a KernelTask.
        """

        return KernelTask(
            name=context.name,
            payload=context.payload,
            priority=context.priority,
        )