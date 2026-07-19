"""
===============================================================================
Planning → ExecutionGraph Converter
===============================================================================
"""
from __future__ import annotations

from typing import Dict, List, Set

from hermes.planning.plan import Plan, PlanStep
from hermes.planning.exceptions import PlanningError
from hermes.reasoning.execution_graph import ExecutionGraph
from hermes.reasoning.execution_node import ExecutionNode
from hermes.reasoning.execution_edge import ExecutionEdge


class PlanToExecutionGraphConverter:
    """
    Converts a Planning Plan into an ExecutionGraph consumable by the Scheduler.
    Each PlanStep becomes an ExecutionNode, and depends_on becomes ExecutionEdges.
    """

    def convert(self, plan: Plan) -> ExecutionGraph:
        """
        Convert a Plan into an ExecutionGraph.

        Raises:
            PlanningError: If the plan is empty, contains duplicate step IDs,
                or contains invalid dependencies.
        """
        if not plan.steps:
            raise PlanningError("Cannot convert an empty Plan to ExecutionGraph")

        # Check for duplicate step IDs
        step_ids: Set[str] = set()
        for step in plan.steps:
            if step.id in step_ids:
                raise PlanningError(f"Duplicate step ID found: {step.id}")
            step_ids.add(step.id)

        # Map step.id -> step for quick lookup
        step_map: Dict[str, PlanStep] = {step.id: step for step in plan.steps}

        # Create nodes
        nodes: List[ExecutionNode] = []
        for step in plan.steps:
            # Use domain as node name for readable logs
            name = step.domain.value
            # The task is the domain's capability
            task = step.domain.value
            # Payload is the instruction
            payload = step.instruction
            # Copy only step.metadata; do not add extra keys
            metadata = step.metadata.copy()

            node = ExecutionNode(
                id=step.id,
                name=name,
                task=task,
                payload=payload,
                # priority, capability, provider, model left to defaults or later resolution
                metadata=metadata,
            )
            nodes.append(node)

        # Create edges based on depends_on
        edges: List[ExecutionEdge] = []
        for step in plan.steps:
            if step.depends_on:
                # Ensure all dependencies exist
                for dep_id in step.depends_on:
                    if dep_id not in step_map:
                        raise PlanningError(
                            f"Step '{step.id}' depends on unknown step '{dep_id}'"
                        )
                    # Edge from dependency to current step
                    edges.append(ExecutionEdge(source=dep_id, target=step.id))

        # Build and return the ExecutionGraph
        graph = ExecutionGraph()
        for node in nodes:
            graph.add_node(node)
        for edge in edges:
            graph.add_edge(edge)

        # Basic validation: ensure we don't have cycles
        self._validate_acyclic(graph)

        return graph

    def _validate_acyclic(self, graph: ExecutionGraph) -> None:
        """
        Perform a simple cycle detection. Raises PlanningError if a cycle is found.
        """
        visited: Set[str] = set()
        recursion_stack: Set[str] = set()

        def detect_cycle(node_id: str) -> bool:
            if node_id in recursion_stack:
                return True
            if node_id in visited:
                return False
            visited.add(node_id)
            recursion_stack.add(node_id)
            # Get outgoing edges (where source == node_id)
            for edge in graph.all_edges():
                if edge.source == node_id:
                    if detect_cycle(edge.target):
                        return True
            recursion_stack.remove(node_id)
            return False

        for node in graph.all_nodes():
            if node.id not in visited:
                if detect_cycle(node.id):
                    raise PlanningError("Cycle detected in Plan dependencies")