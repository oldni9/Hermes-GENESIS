"""
===============================================================================
Hermes Task Builder Mapper

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.reasoning.execution_node import ExecutionNode
from hermes.taskbuilder.context import TaskBuilderContext


class TaskBuilderMapper:
    """
    Maps an ExecutionNode into a TaskBuilderContext.
    """

    def map(
        self,
        node: ExecutionNode,
    ) -> TaskBuilderContext:

        return TaskBuilderContext(
            name=node.name,
            payload=node.payload,
            priority=node.priority,
        )
