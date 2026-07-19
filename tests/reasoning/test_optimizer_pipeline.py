"""
===============================================================================
Integration Test: Planning → Optimizer → Scheduler Pipeline
===============================================================================
Verifies that the full pipeline works with the optimizer integrated:

    Planner
        ↓
    PlanToExecutionGraphConverter
        ↓
    ExecutionGraph
        ↓
    GraphOptimizer
        ↓
    OptimizedGraph
        ↓
    SchedulerEngine
===============================================================================
"""
from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from hermes.planning import (
    Planner,
    PipelinePlanningBackend,
    PlanToExecutionGraphConverter,
)
from hermes.reasoning.optimizer import GraphOptimizer
from hermes.scheduler.engine import SchedulerEngine
from hermes.reasoning.execution_graph import ExecutionGraph


@pytest.fixture
def mock_backend() -> MagicMock:
    mock = MagicMock(spec=PipelinePlanningBackend)
    # Return a plan with a redundant edge: A -> B, A -> C, B -> C
    mock.generate_plan.return_value = json.dumps([
        {"id": "A", "domain": "search", "instruction": "Search"},
        {"id": "B", "domain": "summarize", "instruction": "Summarize", "depends_on": ["A"]},
        {"id": "C", "domain": "chat", "instruction": "Explain", "depends_on": ["A", "B"]},
    ])
    return mock


def test_planning_to_scheduler_with_optimizer(mock_backend: MagicMock) -> None:
    """
    Test the full pipeline with optimizer enabled.
    The plan contains a redundant edge A->C which should be removed.
    """
    # 1. Planner
    planner = Planner(mock_backend)
    plan = planner.plan("Research and summarize")

    # 2. Converter
    converter = PlanToExecutionGraphConverter()
    graph = converter.convert(plan)

    # 3. Optimizer
    optimizer = GraphOptimizer()
    result = optimizer.optimize(graph)
    optimized_graph = result.graph

    # Verify the redundant edge was removed: A->C should be gone
    nodes = optimized_graph.all_nodes()
    edges = optimized_graph.all_edges()
    assert len(nodes) == 3
    assert len(edges) == 2
    # Check that only A->B and B->C remain
    edge_pairs = {(e.source, e.target) for e in edges}
    assert edge_pairs == {("A", "B"), ("B", "C")}
    assert ("A", "C") not in edge_pairs

    # 4. Scheduler (no optimizer parameter)
    scheduler = SchedulerEngine()
    processed_graph = scheduler.process(optimized_graph)

    # Verify the graph was processed correctly
    assert isinstance(processed_graph, ExecutionGraph)
    # Metadata is available via result
    assert result.metadata is not None
    assert result.metadata["critical_path_length"] == 3
    assert result.metadata["node_count"] == 3