"""
===============================================================================
Integration Test: Planning → ExecutionGraph Pipeline
===============================================================================
Verifies that the planning subsystem produces a valid ExecutionGraph
when given a multi-step plan via a mocked PlanningBackend.

This is an integration test, not a unit test.
It ensures that the following components work together:

    PlanningBackend (mocked)
        ↓
    Planner.plan()
        ↓
    Plan
        ↓
    PlanToExecutionGraphConverter
        ↓
    ExecutionGraph

No production code is modified. The test uses a mocked backend that
returns a controlled JSON plan.
===============================================================================
"""
from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from hermes.planning import (
    Planner,
    PlanningBackend,
    PlanToExecutionGraphConverter,
)
from hermes.planning.domain import Domain
from hermes.reasoning.execution_graph import ExecutionGraph


@pytest.fixture
def mock_backend() -> MagicMock:
    """Create a mock backend that returns a valid multi-step JSON plan."""
    mock = MagicMock(spec=PlanningBackend)
    mock.generate_plan.return_value = json.dumps([
        {
            "id": "step1",
            "domain": "search",
            "instruction": "Search for AI GPUs",
        },
        {
            "id": "step2",
            "domain": "summarize",
            "instruction": "Summarize results",
            "depends_on": ["step1"],
        },
    ])
    return mock


def test_planning_to_execution_graph_integration(mock_backend: MagicMock) -> None:
    """
    Test the complete pipeline from Plan to ExecutionGraph.
    """
    # ------------------------------------------------------------------
    # 1. Create Planner and generate a Plan
    # ------------------------------------------------------------------
    planner = Planner(mock_backend)
    plan = planner.plan("Research AI GPUs and summarize")

    # Verify the Plan structure
    assert len(plan.steps) == 2
    step1 = plan.steps[0]
    step2 = plan.steps[1]

    assert step1.id == "step1"
    assert step1.domain == Domain.SEARCH
    assert step1.instruction == "Search for AI GPUs"
    assert step1.depends_on == []

    assert step2.id == "step2"
    assert step2.domain == Domain.SUMMARIZE
    assert step2.instruction == "Summarize results"
    assert step2.depends_on == ["step1"]

    # ------------------------------------------------------------------
    # 2. Convert Plan to ExecutionGraph
    # ------------------------------------------------------------------
    converter = PlanToExecutionGraphConverter()
    graph = converter.convert(plan)

    # Verify the ExecutionGraph structure
    assert isinstance(graph, ExecutionGraph)

    nodes = graph.all_nodes()
    edges = graph.all_edges()

    assert len(nodes) == 2
    assert len(edges) == 1

    # Check nodes by ID
    node1 = graph.get_node("step1")
    node2 = graph.get_node("step2")

    assert node1 is not None
    assert node2 is not None

    assert node1.id == "step1"
    assert node1.task == "search"
    assert node1.payload == "Search for AI GPUs"
    assert node1.name == "search"

    assert node2.id == "step2"
    assert node2.task == "summarize"
    assert node2.payload == "Summarize results"
    assert node2.name == "summarize"

    # Check edge
    assert edges[0].source == "step1"
    assert edges[0].target == "step2"

    # ------------------------------------------------------------------
    # 3. Verify graph is acyclic (no exception should be raised)
    # ------------------------------------------------------------------
    # The conversion already validated acyclicity; we can re-run conversion
    # to confirm it succeeds.
    converter.convert(plan)  # no exception means graph is valid