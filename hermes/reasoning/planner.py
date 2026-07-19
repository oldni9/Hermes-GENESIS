"""
===============================================================================
Hermes Reasoning Planner

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from uuid import uuid4

from hermes.executive.decision import ExecutiveDecision
from hermes.reasoning.execution_graph import ExecutionGraph
from hermes.reasoning.execution_node import ExecutionNode


class ReasoningPlanner:
    """
    Builds an ExecutionGraph from an ExecutiveDecision.
    """

    def build(
        self,
        decision: ExecutiveDecision,
    ) -> ExecutionGraph:

        graph = ExecutionGraph()

        node = ExecutionNode(
            id=str(uuid4()),
            name="primary",
            task="chat",
            payload=decision.prompt,
            priority=50,
        )

        graph.add_node(
            node,
        )

        return graph
