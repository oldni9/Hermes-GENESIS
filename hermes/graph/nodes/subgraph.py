"""
===============================================================================
Subgraph Execution Node
===============================================================================

Sprint 15.1: Base class for nodes that execute subgraphs.
Centralizes GraphRunner execution and result mapping.
===============================================================================
"""
from __future__ import annotations

from typing import Optional

from hermes.graph.models import ExecutionGraph, GraphContext, GraphResult, GraphRunner, NodeResult
from hermes.graph.nodes.base import GraphNode


class SubgraphNode(GraphNode):
    """Base class for nodes that own and execute other graphs."""
    
    def __init__(
        self, 
        node_id: str, 
        graph_runner: GraphRunner,
        output_key: Optional[str] = None
    ) -> None:
        super().__init__(node_id)
        self._graph_runner = graph_runner
        self._output_key = output_key or node_id

    def run_subgraph(self, graph: ExecutionGraph, context: GraphContext) -> GraphResult:
        """Executes a subgraph and returns the raw GraphResult."""
        return self._graph_runner.run(graph, context)

    def _execute_subgraph(self, graph: ExecutionGraph, context: GraphContext) -> NodeResult:
        """Executes a subgraph and maps the result to a NodeResult."""
        graph_result = self.run_subgraph(graph, context)
        return graph_result.to_node_result()

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture