"""
===============================================================================
Tests for Agent Runtime
===============================================================================
"""
from __future__ import annotations

from unittest.mock import MagicMock
import pytest

from hermes.agent.runtime import AgentRuntime
from hermes.agent.agent import Agent
from hermes.agent.exceptions import AgentNotFound
from hermes.planning.planner import Planner
from hermes.planning.plan_to_execution_graph import PlanToExecutionGraphConverter
from hermes.scheduler.engine import SchedulerEngine


@pytest.fixture
def mock_planner() -> MagicMock:
    return MagicMock(spec=Planner)


@pytest.fixture
def mock_converter() -> MagicMock:
    return MagicMock(spec=PlanToExecutionGraphConverter)


@pytest.fixture
def mock_scheduler() -> MagicMock:
    return MagicMock(spec=SchedulerEngine)


@pytest.fixture
def runtime(mock_planner, mock_converter, mock_scheduler) -> AgentRuntime:
    return AgentRuntime(
        planner=mock_planner,
        converter=mock_converter,
        scheduler=mock_scheduler,
    )


def test_create_agent(runtime: AgentRuntime):
    agent = runtime.create_agent("test prompt")
    assert isinstance(agent, Agent)
    assert agent.id is not None
    assert agent.system_prompt == "test prompt"
    assert len(runtime.list_agents()) == 1


def test_create_agent_with_id(runtime: AgentRuntime):
    agent = runtime.create_agent("test", agent_id="custom")
    assert agent.id == "custom"


def test_get_agent(runtime: AgentRuntime):
    agent = runtime.create_agent("test")
    retrieved = runtime.get_agent(agent.id)
    assert retrieved is agent


def test_get_agent_not_found(runtime: AgentRuntime):
    assert runtime.get_agent("nonexistent") is None


def test_list_agents(runtime: AgentRuntime):
    runtime.create_agent("a")
    runtime.create_agent("b")
    agents = runtime.list_agents()
    assert len(agents) == 2


def test_destroy_agent(runtime: AgentRuntime):
    agent = runtime.create_agent("test")
    runtime.destroy_agent(agent.id)
    assert len(runtime.list_agents()) == 0
    with pytest.raises(AgentNotFound):
        runtime.destroy_agent(agent.id)


def test_reset_session(runtime: AgentRuntime):
    agent = runtime.create_agent("test")
    old_session = agent.session
    runtime.reset_session(agent.id)
    assert agent.session is not old_session


def test_reset_session_not_found(runtime: AgentRuntime):
    with pytest.raises(AgentNotFound):
        runtime.reset_session("nonexistent")


def test_execute(mock_planner, mock_converter, mock_scheduler, runtime):
    # Setup mocks to simulate a simple plan
    from hermes.planning.plan import Plan, PlanStep
    from hermes.planning.domain import Domain
    from hermes.reasoning.execution_graph import ExecutionGraph
    from hermes.reasoning.execution_node import ExecutionNode

    mock_plan = Plan(steps=[PlanStep(domain=Domain.CHAT, instruction="hello")])
    mock_planner.plan.return_value = mock_plan

    mock_graph = ExecutionGraph()
    node = ExecutionNode(id="node1", name="chat", task="chat", payload="Hello response")
    mock_graph.add_node(node)
    mock_converter.convert.return_value = mock_graph

    mock_scheduler.process.return_value = mock_graph

    agent = runtime.create_agent("test")
    response = runtime.execute(agent, "hello")

    assert response.success is True
    assert response.text == "Hello response"
    assert response.session is agent.session
    assert response.plan is not None
    assert response.execution_graph is not None