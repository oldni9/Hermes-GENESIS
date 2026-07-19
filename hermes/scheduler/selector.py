"""
===============================================================================
Hermes Scheduler Selector

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.reasoning.execution_graph import ExecutionGraph
from hermes.reasoning.execution_node import ExecutionNode


class SchedulerSelector:
    """
    Selects executable nodes.

    Genesis:
        returns every incomplete node.

    Future:
        dependency aware
        cost aware
        trust aware
        parallel aware
    """

    def select(
        self,
        graph: ExecutionGraph,
    ) -> list[ExecutionNode]:

        return [node for node in graph.all_nodes() if not node.completed]
