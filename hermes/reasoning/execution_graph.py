"""
===============================================================================
Hermes Execution Graph (DAG)

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.reasoning.execution_edge import ExecutionEdge
from hermes.reasoning.execution_node import ExecutionNode


class ExecutionGraph:
    """
    Directed Acyclic Graph used by Hermes.

    Every request becomes an ExecutionGraph.
    """

    def __init__(self) -> None:

        self.nodes: dict[str, ExecutionNode] = {}

        self.edges: list[ExecutionEdge] = []

    # ------------------------------------------------------------------

    def add_node(
        self,
        node: ExecutionNode,
    ) -> None:

        self.nodes[node.id] = node

    # ------------------------------------------------------------------

    def add_edge(
        self,
        edge: ExecutionEdge,
    ) -> None:

        self.edges.append(edge)

    # ------------------------------------------------------------------

    def get_node(
        self,
        node_id: str,
    ) -> ExecutionNode | None:

        return self.nodes.get(node_id)

    # ------------------------------------------------------------------

    def all_nodes(
        self,
    ) -> list[ExecutionNode]:

        return list(self.nodes.values())

    # ------------------------------------------------------------------

    def all_edges(
        self,
    ) -> list[ExecutionEdge]:

        return list(self.edges)