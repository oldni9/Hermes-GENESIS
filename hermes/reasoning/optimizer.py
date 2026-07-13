"""
===============================================================================
Hermes Reasoning Optimizer

Optimizes an Execution Graph.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.reasoning.execution_graph import ExecutionGraph


class ReasoningOptimizer:
    """
    Optimizes execution graphs.

    Future versions will optimize:

        • Cost
        • Trust
        • Latency
        • Parallelism
    """

    def optimize(
        self,
        graph: ExecutionGraph,
    ) -> ExecutionGraph:

        return graph