"""
===============================================================================
Tests for Execution Graph Optimizer
===============================================================================
"""
from __future__ import annotations

import pytest

from hermes.reasoning.execution_graph import ExecutionGraph
from hermes.reasoning.execution_node import ExecutionNode
from hermes.reasoning.execution_edge import ExecutionEdge
from hermes.reasoning.optimizer import GraphOptimizer, OptimizationResult
from hermes.reasoning.exceptions import GraphValidationError


@pytest.fixture
def optimizer() -> GraphOptimizer:
    return GraphOptimizer()


def test_validate_valid_graph(optimizer: GraphOptimizer):
    graph = ExecutionGraph()
    graph.add_node(ExecutionNode(id="A", name="A", task="task"))
    graph.add_node(ExecutionNode(id="B", name="B", task="task"))
    graph.add_node(ExecutionNode(id="C", name="C", task="task"))
    graph.add_edge(ExecutionEdge(source="A", target="B"))
    graph.add_edge(ExecutionEdge(source="B", target="C"))
    optimizer.validate(graph)  # should not raise


def test_validate_missing_dependency(optimizer: GraphOptimizer):
    graph = ExecutionGraph()
    graph.add_node(ExecutionNode(id="A", name="A", task="task"))
    graph.add_node(ExecutionNode(id="B", name="B", task="task"))
    graph.add_edge(ExecutionEdge(source="A", target="C"))  # C does not exist
    with pytest.raises(GraphValidationError, match="Edge target 'C' does not exist"):
        optimizer.validate(graph)


def test_validate_cycle(optimizer: GraphOptimizer):
    graph = ExecutionGraph()
    graph.add_node(ExecutionNode(id="A", name="A", task="task"))
    graph.add_node(ExecutionNode(id="B", name="B", task="task"))
    graph.add_edge(ExecutionEdge(source="A", target="B"))
    graph.add_edge(ExecutionEdge(source="B", target="A"))
    with pytest.raises(GraphValidationError, match="Graph contains a cycle"):
        optimizer.validate(graph)


def test_remove_redundant_edges(optimizer: GraphOptimizer):
    graph = ExecutionGraph()
    graph.add_node(ExecutionNode(id="A", name="A", task="task"))
    graph.add_node(ExecutionNode(id="B", name="B", task="task"))
    graph.add_node(ExecutionNode(id="C", name="C", task="task"))
    graph.add_edge(ExecutionEdge(source="A", target="B"))
    graph.add_edge(ExecutionEdge(source="A", target="C"))
    graph.add_edge(ExecutionEdge(source="B", target="C"))

    optimized = optimizer.remove_redundant_edges(graph)
    edges = optimized.all_edges()
    # Should remove A->C because A->B->C exists
    assert len(edges) == 2
    # Depending on order, we need to check that the remaining edges are A->B and B->C
    sources_targets = {(e.source, e.target) for e in edges}
    assert ("A", "B") in sources_targets
    assert ("B", "C") in sources_targets
    assert ("A", "C") not in sources_targets


def test_topological_order(optimizer: GraphOptimizer):
    graph = ExecutionGraph()
    graph.add_node(ExecutionNode(id="A", name="A", task="task"))
    graph.add_node(ExecutionNode(id="B", name="B", task="task"))
    graph.add_node(ExecutionNode(id="C", name="C", task="task"))
    graph.add_node(ExecutionNode(id="D", name="D", task="task"))
    graph.add_edge(ExecutionEdge(source="A", target="B"))
    graph.add_edge(ExecutionEdge(source="A", target="C"))
    graph.add_edge(ExecutionEdge(source="B", target="D"))
    graph.add_edge(ExecutionEdge(source="C", target="D"))

    levels = optimizer.topological_order(graph)
    # Expected: [["A"], ["B", "C"], ["D"]]
    assert len(levels) == 3
    assert set(levels[0]) == {"A"}
    assert set(levels[1]) == {"B", "C"}
    assert set(levels[2]) == {"D"}


def test_critical_path_length(optimizer: GraphOptimizer):
    graph = ExecutionGraph()
    graph.add_node(ExecutionNode(id="A", name="A", task="task"))
    graph.add_node(ExecutionNode(id="B", name="B", task="task"))
    graph.add_node(ExecutionNode(id="C", name="C", task="task"))
    graph.add_edge(ExecutionEdge(source="A", target="B"))
    graph.add_edge(ExecutionEdge(source="B", target="C"))

    length = optimizer.critical_path_length(graph)
    assert length == 3


def test_statistics(optimizer: GraphOptimizer):
    graph = ExecutionGraph()
    graph.add_node(ExecutionNode(id="A", name="A", task="task"))
    graph.add_node(ExecutionNode(id="B", name="B", task="task"))
    graph.add_node(ExecutionNode(id="C", name="C", task="task"))
    graph.add_edge(ExecutionEdge(source="A", target="B"))
    graph.add_edge(ExecutionEdge(source="A", target="C"))

    stats = optimizer.statistics(graph)
    assert stats["node_count"] == 3
    assert stats["edge_count"] == 2
    assert stats["root_count"] == 1
    assert stats["leaf_count"] == 2
    assert stats["depth"] == 2
    assert len(stats["parallel_groups"]) == 2


def test_optimize(optimizer: GraphOptimizer):
    graph = ExecutionGraph()
    graph.add_node(ExecutionNode(id="A", name="A", task="task"))
    graph.add_node(ExecutionNode(id="B", name="B", task="task"))
    graph.add_node(ExecutionNode(id="C", name="C", task="task"))
    graph.add_edge(ExecutionEdge(source="A", target="B"))
    graph.add_edge(ExecutionEdge(source="A", target="C"))
    graph.add_edge(ExecutionEdge(source="B", target="C"))

    result = optimizer.optimize(graph)
    assert isinstance(result, OptimizationResult)
    assert isinstance(result.graph, ExecutionGraph)
    # Redundant edge should be removed
    assert len(result.graph.all_edges()) == 2
    assert "critical_path_length" in result.metadata
    assert result.metadata["node_count"] == 3
    assert result.metadata["edge_count"] == 2


def test_redundant_edge_removal_preserves_order(optimizer: GraphOptimizer):
    # Graph: A -> B, A -> C, B -> C
    graph = ExecutionGraph()
    graph.add_node(ExecutionNode(id="A", name="A", task="task"))
    graph.add_node(ExecutionNode(id="B", name="B", task="task"))
    graph.add_node(ExecutionNode(id="C", name="C", task="task"))
    graph.add_edge(ExecutionEdge(source="A", target="B"))
    graph.add_edge(ExecutionEdge(source="A", target="C"))
    graph.add_edge(ExecutionEdge(source="B", target="C"))

    optimized = optimizer.remove_redundant_edges(graph)
    # Redundant edge A->C should be removed
    edges = optimized.all_edges()
    assert len(edges) == 2
    # But the reachability must remain: A can reach C via B
    # We can check that topological order is the same
    levels = optimizer.topological_order(optimized)
    # Should be [["A"], ["B"], ["C"]] or [["A"], ["B", "C"]] depending on parallel
    # Since we have A->B and B->C, the order is A, B, C
    assert levels == [["A"], ["B"], ["C"]]