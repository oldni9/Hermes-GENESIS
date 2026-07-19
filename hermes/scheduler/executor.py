"""
===============================================================================
Hermes Scheduler Executor

Executes scheduled nodes.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.reasoning.execution_node import ExecutionNode


class SchedulerExecutor:
    """
    Executes scheduler tasks.

    Genesis implementation simply
    marks nodes as completed.
    """

    def execute(
        self,
        node: ExecutionNode,
    ) -> ExecutionNode:

        node.completed = True

        return node
