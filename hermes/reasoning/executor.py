"""
===============================================================================
Hermes Reasoning Executor

Executes an Execution Graph.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.reasoning.execution_graph import ExecutionGraph


class ReasoningExecutor:
    """
    Executes an execution graph.

    Genesis implementation simply
    returns the graph.
    """

    def execute(
        self,
        graph: ExecutionGraph,
    ) -> ExecutionGraph:

        return graph
