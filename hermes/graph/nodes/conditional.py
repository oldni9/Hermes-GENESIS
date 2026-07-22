"""
===============================================================================
Conditional Routing Node
===============================================================================

Sprint 15.1 Update:
Inherits from SubgraphNode.
Uses GraphRunner type hint.
===============================================================================
"""
from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from hermes.graph.models import ExecutionGraph, GraphContext, GraphRunner, NodeResult
from hermes.graph.nodes.subgraph import SubgraphNode


class RouterNode(SubgraphNode):
    """
    Evaluates a predicate against the blackboard and executes the corresponding
    subgraph. This keeps routing semantics inside nodes, leaving the executor frozen.
    """
    
    def __init__(
        self, 
        node_id: str, 
        routes: Dict[str, ExecutionGraph],
        predicate: Callable[[Dict[str, Any]], str],
        graph_runner: GraphRunner,
        default_route: Optional[str] = None,
        output_key: str = "text"
    ) -> None:
        super().__init__(node_id, graph_runner, output_key)
        self._routes = routes
        self._predicate = predicate
        self._default_route = default_route

    def execute(self, context: GraphContext) -> NodeResult:
        blackboard_dict = context.blackboard.to_dict()
        
        selected_route = self._predicate(blackboard_dict)
        
        if selected_route not in self._routes:
            if self._default_route and self._default_route in self._routes:
                selected_route = self._default_route
            else:
                return NodeResult(
                    success=False, 
                    stop=True, 
                    outputs={"error": f"Route '{selected_route}' not found and no valid default."}
                )
                
        selected_graph = self._routes[selected_route]
        
        # Execute the selected subgraph using the centralized SubgraphNode logic
        return self._execute_subgraph(selected_graph, context)

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture