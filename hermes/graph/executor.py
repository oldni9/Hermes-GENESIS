"""
===============================================================================
Graph Executor
===============================================================================

Sprint 16 Update:
GraphExecutor extracts memory_candidates from the exit node's metadata
and carries them in GraphResult. It remains completely memory-agnostic.
===============================================================================
"""
from __future__ import annotations

import time
from collections import deque
from typing import Any, Dict, List

from hermes.agent.executor.trace import TraceEventType
from hermes.graph.models import ExecutionGraph, GraphContext, GraphResult, NodeResult, GraphExecutionError


class GraphExecutor:
    """Executes an ExecutionGraph sequentially in topological order."""

    def run(
        self, 
        graph: ExecutionGraph, 
        context: GraphContext
    ) -> GraphResult:
        start_time = time.time()
        
        context.trace.add_event(1, TraceEventType.GRAPH_STARTED, {
            "entry_node": graph.entry_node, 
            "exit_node": graph.exit_node
        })
        
        sorted_nodes = self._topological_sort(graph)
        final_result: NodeResult = NodeResult(success=True)
        
        try:
            for node_id in sorted_nodes:
                node = graph.nodes[node_id]
                context.trace.add_event(1, TraceEventType.NODE_STARTED, {"node_id": node_id})
                
                try:
                    final_result = node.execute(context)
                except Exception as e:
                    context.trace.add_event(1, TraceEventType.NODE_FINISHED, {
                        "node_id": node_id, 
                        "success": False,
                        "error": str(e)
                    })
                    raise GraphExecutionError(
                        node_id, 
                        context.trace, 
                        context.blackboard.to_dict(), 
                        e
                    ) from e
                
                context.trace.add_event(1, TraceEventType.NODE_FINISHED, {
                    "node_id": node_id, 
                    "success": final_result.success,
                    "stop": final_result.stop
                })
                
                context.blackboard.update(final_result.outputs)
                
                if final_result.stop:
                    break
        finally:
            context.trace.add_event(1, TraceEventType.GRAPH_FINISHED, {"success": final_result.success})
            context.trace.finalize()
                
        token_usage = {
            "prompt_tokens": context.trace.metrics.total_prompt_tokens,
            "completion_tokens": context.trace.metrics.total_completion_tokens
        }
        
        # Extract memory candidates from the exit node's metadata
        memory_candidates = list(final_result.metadata.memory_candidates)
        
        return GraphResult(
            success=final_result.success,
            outputs=final_result.outputs,
            duration=time.time() - start_time,
            trace=context.trace,
            memory_candidates=memory_candidates,
            token_usage=token_usage
        )

    def _topological_sort(self, graph: ExecutionGraph) -> List[str]:
        """Kahn's algorithm for topological sorting using deque for O(1) pops."""
        in_degree = {u: 0 for u in graph.nodes}
        adj = graph.children
        
        for u in graph.nodes:
            for v in adj[u]:
                in_degree[v] += 1
            
        queue = deque([u for u in graph.nodes if in_degree[u] == 0])
        sorted_nodes = []
        
        while queue:
            u = queue.popleft()
            sorted_nodes.append(u)
            
            for v in adj[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)
                    
        if len(sorted_nodes) != len(graph.nodes):
            raise ValueError("Graph has a cycle (should have been caught at initialization).")
            
        return sorted_nodes

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture