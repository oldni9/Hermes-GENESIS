"""
===============================================================================
Tests for Planning → ExecutionGraph Converter
===============================================================================
"""
from __future__ import annotations

import pytest

from hermes.planning.domain import Domain
from hermes.planning.plan import Plan, PlanStep
from hermes.planning.plan_to_execution_graph import PlanToExecutionGraphConverter
from hermes.planning.exceptions import PlanningError
from hermes.reasoning.execution_graph import ExecutionGraph
from hermes.reasoning.execution_node import ExecutionNode
from hermes.reasoning.execution_edge import ExecutionEdge


@pytest.fixture
def converter() -> PlanToExecutionGraphConverter:
    return PlanToExecutionGraphConverter()


def test_convert_single_step(converter: PlanToExecutionGraphConverter):
    step = PlanStep(domain=Domain.CHAT, instruction="Hello")
    plan = Plan(steps=[step])

    graph = converter.convert(plan)

    assert isinstance(graph, ExecutionGraph)
    nodes = graph.all_nodes()
    assert len(nodes) == 1
    node = nodes[0]
    assert node.id == step.id
    assert node.name == "chat"  # domain value
    assert node.task == "chat"
    assert node.payload == "Hello"
    assert "domain" not in node.metadata
    assert "instruction" not in node.metadata
    edges = graph.all_edges()
    assert len(edges) == 0


def test_convert_multiple_steps(converter: PlanToExecutionGraphConverter):
    steps = [
        PlanStep(domain=Domain.CODE, instruction="Write code"),
        PlanStep(domain=Domain.SUMMARIZE, instruction="Summarize"),
    ]
    plan = Plan(steps=steps)

    graph = converter.convert(plan)

    nodes = graph.all_nodes()
    assert len(nodes) == 2
    assert nodes[0].name == "code"
    assert nodes[1].name == "summarize"
    assert nodes[0].task == "code"
    assert nodes[1].task == "summarize"
    assert len(graph.all_edges()) == 0


def test_convert_with_dependencies(converter: PlanToExecutionGraphConverter):
    step1 = PlanStep(domain=Domain.CODE, instruction="Write code", id="step1")
    step2 = PlanStep(
        domain=Domain.SUMMARIZE,
        instruction="Summarize",
        depends_on=["step1"],
        id="step2",
    )
    plan = Plan(steps=[step1, step2])

    graph = converter.convert(plan)

    nodes = graph.all_nodes()
    assert len(nodes) == 2
    edges = graph.all_edges()
    assert len(edges) == 1
    assert edges[0].source == "step1"
    assert edges[0].target == "step2"


def test_convert_handles_metadata(converter: PlanToExecutionGraphConverter):
    step = PlanStep(
        domain=Domain.CHAT,
        instruction="Hello",
        metadata={"source": "test"},
    )
    plan = Plan(steps=[step], metadata={"plan": "test"})

    graph = converter.convert(plan)

    node = graph.all_nodes()[0]
    assert node.metadata["source"] == "test"


def test_convert_raises_on_empty_plan(converter: PlanToExecutionGraphConverter):
    plan = Plan(steps=[])
    with pytest.raises(PlanningError, match="empty Plan"):
        converter.convert(plan)


def test_convert_raises_on_unknown_dependency(converter: PlanToExecutionGraphConverter):
    step = PlanStep(
        domain=Domain.CHAT,
        instruction="Hello",
        depends_on=["nonexistent"],
        id="step1",
    )
    plan = Plan(steps=[step])
    with pytest.raises(PlanningError, match="unknown step"):
        converter.convert(plan)


def test_convert_raises_on_cycle(converter: PlanToExecutionGraphConverter):
    step1 = PlanStep(
        domain=Domain.CHAT,
        instruction="A",
        depends_on=["step2"],
        id="step1",
    )
    step2 = PlanStep(
        domain=Domain.CHAT,
        instruction="B",
        depends_on=["step1"],
        id="step2",
    )
    plan = Plan(steps=[step1, step2])
    with pytest.raises(PlanningError, match="Cycle detected"):
        converter.convert(plan)


def test_convert_raises_on_duplicate_id(converter: PlanToExecutionGraphConverter):
    step1 = PlanStep(domain=Domain.CHAT, instruction="A", id="dup")
    step2 = PlanStep(domain=Domain.CHAT, instruction="B", id="dup")
    plan = Plan(steps=[step1, step2])
    with pytest.raises(PlanningError, match="Duplicate step ID"):
        converter.convert(plan)