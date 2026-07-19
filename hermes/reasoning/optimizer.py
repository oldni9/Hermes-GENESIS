"""
===============================================================================
Execution Graph Optimizer
===============================================================================
"""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any, Dict, List, Set, Tuple

from hermes.reasoning.execution_graph import ExecutionGraph
from hermes.reasoning.execution_node import ExecutionNode
from hermes.reasoning.execution_edge import ExecutionEdge
from hermes.reasoning.exceptions import GraphValidationError, GraphOptimizationError


@dataclass(slots=True)
class OptimizationResult:
    """
    Result of optimizing an ExecutionGraph.
    Contains the optimized graph and optimization metadata.
    """
    graph: ExecutionGraph
    metadata: Dict[str, Any] = field(default_factory=dict)


class GraphOptimizer:
    """
    Performs validation and optimization on ExecutionGraphs.
    All operations are provider-agnostic and do not execute anything.
    """

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self, graph: ExecutionGraph) -> None:
        """
        Validate the graph for missing dependencies and cycles.
        Duplicate IDs are assumed to be prevented by ExecutionGraph.
        Raises GraphValidationError if any issue is found.
        """
        nodes = graph.all_nodes()
        edges = graph.all_edges()

        # Collect all node IDs
        node_ids = {node.id for node in nodes}

        # Check that every edge references existing nodes
        for edge in edges:
            if edge.source not in node_ids:
                raise GraphValidationError(f"Edge source '{edge.source}' does not exist")
            if edge.target not in node_ids:
                raise GraphValidationError(f"Edge target '{edge.target}' does not exist")

        # Check for cycles using DFS
        visited: Set[str] = set()
        recursion_stack: Set[str] = set()

        def detect_cycle(node_id: str) -> None:
            if node_id in recursion_stack:
                raise GraphValidationError("Graph contains a cycle")
            if node_id in visited:
                return
            visited.add(node_id)
            recursion_stack.add(node_id)
            for edge in edges:
                if edge.source == node_id:
                    detect_cycle(edge.target)
            recursion_stack.remove(node_id)

        for node in nodes:
            if node.id not in visited:
                detect_cycle(node.id)

    # ------------------------------------------------------------------
    # Redundant Edge Removal
    # ------------------------------------------------------------------

    def remove_redundant_edges(self, graph: ExecutionGraph) -> ExecutionGraph:
        """
        Remove transitive edges (e.g., if A→B and B→C, remove A→C).
        Returns a new ExecutionGraph with redundant edges removed.
        """
        self.validate(graph)

        nodes = graph.all_nodes()
        edges = graph.all_edges()

        # Build adjacency list for reachability checks
        adj: Dict[str, List[str]] = defaultdict(list)
        for edge in edges:
            adj[edge.source].append(edge.target)

        # Function to check if there is a path from src to dst using only edges in adj
        def has_path(src: str, dst: str, avoid: Tuple[str, str]) -> bool:
            visited: Set[str] = set()
            queue = deque([src])
            while queue:
                curr = queue.popleft()
                if curr == dst:
                    return True
                if curr in visited:
                    continue
                visited.add(curr)
                for nxt in adj.get(curr, []):
                    # Do not use the edge we are avoiding
                    if (curr, nxt) == avoid:
                        continue
                    if nxt not in visited:
                        queue.append(nxt)
            return False

        # Determine which edges are redundant
        necessary_edges: List[ExecutionEdge] = []
        for edge in edges:
            # Check if there is an alternative path from edge.source to edge.target
            if not has_path(edge.source, edge.target, (edge.source, edge.target)):
                necessary_edges.append(edge)

        # Build new graph with necessary edges
        new_graph = ExecutionGraph()
        for node in nodes:
            new_graph.add_node(node)
        for edge in necessary_edges:
            new_graph.add_edge(edge)

        return new_graph

    # ------------------------------------------------------------------
    # Topological Ordering & Parallel Groups
    # ------------------------------------------------------------------

    def topological_order(self, graph: ExecutionGraph) -> List[List[str]]:
        """
        Returns a list of levels, where each level is a list of node IDs that
        can be executed in parallel. Raises GraphValidationError if the graph
        contains a cycle.
        """
        self.validate(graph)

        nodes = graph.all_nodes()
        edges = graph.all_edges()

        # Build adjacency and in-degree
        adj: Dict[str, List[str]] = defaultdict(list)
        in_degree: Dict[str, int] = defaultdict(int)

        for node in nodes:
            in_degree[node.id] = 0

        for edge in edges:
            adj[edge.source].append(edge.target)
            in_degree[edge.target] += 1

        # Kahn's algorithm
        queue = deque([nid for nid, deg in in_degree.items() if deg == 0])
        levels: List[List[str]] = []

        while queue:
            level_nodes: List[str] = []
            for _ in range(len(queue)):
                nid = queue.popleft()
                level_nodes.append(nid)
                for neighbor in adj.get(nid, []):
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)
            levels.append(level_nodes)

        # If not all nodes are processed, there is a cycle (should have been caught)
        if sum(len(l) for l in levels) != len(nodes):
            raise GraphValidationError("Graph contains a cycle (unexpected)")

        return levels

    # ------------------------------------------------------------------
    # Critical Path Length
    # ------------------------------------------------------------------

    def critical_path_length(self, graph: ExecutionGraph) -> int:
        """
        Computes the critical path length (number of nodes on the longest path).
        Returns the length as an integer.
        """
        self.validate(graph)

        nodes = graph.all_nodes()
        edges = graph.all_edges()

        # Build adjacency and in-degree
        adj: Dict[str, List[str]] = defaultdict(list)
        in_degree: Dict[str, int] = defaultdict(int)

        for node in nodes:
            in_degree[node.id] = 0

        for edge in edges:
            adj[edge.source].append(edge.target)
            in_degree[edge.target] += 1

        # Compute depth (longest path from any root)
        depth: Dict[str, int] = {node.id: 1 for node in nodes}
        queue = deque([nid for nid, deg in in_degree.items() if deg == 0])

        while queue:
            nid = queue.popleft()
            for neighbor in adj.get(nid, []):
                if depth[neighbor] < depth[nid] + 1:
                    depth[neighbor] = depth[nid] + 1
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        return max(depth.values()) if depth else 0

    # ------------------------------------------------------------------
    # Graph Statistics
    # ------------------------------------------------------------------

    def statistics(self, graph: ExecutionGraph) -> Dict[str, Any]:
        """
        Returns a dictionary of graph statistics.
        """
        self.validate(graph)

        nodes = graph.all_nodes()
        edges = graph.all_edges()

        node_ids = [node.id for node in nodes]
        in_degree = {nid: 0 for nid in node_ids}
        out_degree = {nid: 0 for nid in node_ids}

        for edge in edges:
            in_degree[edge.target] += 1
            out_degree[edge.source] += 1

        roots = [nid for nid, deg in in_degree.items() if deg == 0]
        leaves = [nid for nid, deg in out_degree.items() if deg == 0]

        # Compute depth and parallel groups
        levels = self.topological_order(graph)
        parallel_groups = [level for level in levels]
        depth = len(levels)

        return {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "root_count": len(roots),
            "leaf_count": len(leaves),
            "depth": depth,
            "parallel_groups": parallel_groups,
        }

    # ------------------------------------------------------------------
    # Full Optimization
    # ------------------------------------------------------------------

    def optimize(self, graph: ExecutionGraph) -> OptimizationResult:
        """
        Perform a complete optimization pass:
        1. Validate the graph.
        2. Remove redundant edges.
        3. Compute topological order and parallel groups.
        4. Compute critical path length.
        5. Collect statistics.

        Returns an OptimizationResult containing the optimized graph and metadata.
        """
        # Validate
        self.validate(graph)

        # Remove redundant edges
        optimized_graph = self.remove_redundant_edges(graph)

        # Compute metadata
        levels = self.topological_order(optimized_graph)
        critical_length = self.critical_path_length(optimized_graph)
        stats = self.statistics(optimized_graph)

        metadata = {
            "topological_levels": levels,
            "parallel_groups": [level for level in levels],
            "critical_path_length": critical_length,
            **stats,
        }

        return OptimizationResult(graph=optimized_graph, metadata=metadata)