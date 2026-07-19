"""
===============================================================================
Tests for Planning → Execution Adapter
===============================================================================
"""
from __future__ import annotations

from unittest.mock import MagicMock
import pytest

from hermes.capability.enums import CapabilityType
from hermes.execution.service import ExecutionService
from hermes.providers.result import ProviderResult
from hermes.planning.domain import Domain
from hermes.planning.plan import Plan, PlanStep
from hermes.planning.execution_adapter import PlanExecutor
from hermes.planning.exceptions import PlanningError


@pytest.fixture
def mock_execution_service() -> MagicMock:
    """Mock ExecutionService that returns a successful result."""
    mock = MagicMock(spec=ExecutionService)

    def side_effect(prompt: str, capability: CapabilityType) -> ProviderResult:
        return ProviderResult(success=True, text=f"Result for {prompt}")

    mock.execute.side_effect = side_effect
    return mock


@pytest.fixture
def executor(
    mock_execution_service: MagicMock,
) -> PlanExecutor:
    return PlanExecutor(execution_service=mock_execution_service)


def test_executor_resolves_and_executes_single_step(
    executor: PlanExecutor,
    mock_execution_service: MagicMock,
):
    step = PlanStep(domain=Domain.CHAT, instruction="Hello")
    plan = Plan(steps=[step])

    results = executor.execute(plan)

    assert len(results) == 1
    assert results[0].success is True
    assert results[0].text == "Result for Hello"
    mock_execution_service.execute.assert_called_once_with(
        prompt="Hello",
        capability=CapabilityType.CHAT,
    )


def test_executor_executes_multiple_steps(
    executor: PlanExecutor,
    mock_execution_service: MagicMock,
):
    steps = [
        PlanStep(domain=Domain.CODE, instruction="Write code"),
        PlanStep(domain=Domain.SUMMARIZE, instruction="Summarize"),
    ]
    plan = Plan(steps=steps)

    results = executor.execute(plan)

    assert len(results) == 2
    assert results[0].success is True
    assert results[1].success is True
    assert mock_execution_service.execute.call_count == 2
    mock_execution_service.execute.assert_any_call(
        prompt="Write code",
        capability=CapabilityType.CODE,
    )
    mock_execution_service.execute.assert_any_call(
        prompt="Summarize",
        capability=CapabilityType.CHAT,
    )


def test_executor_raises_on_unknown_domain(
    mock_execution_service: MagicMock,
):
    # Use a custom mapping that omits SEARCH
    custom_mapping = {
        Domain.CHAT: CapabilityType.CHAT,
        Domain.CODE: CapabilityType.CODE,
        Domain.SEARCH: None,
    }
    executor = PlanExecutor(
        execution_service=mock_execution_service,
        mapping=custom_mapping,
    )
    step = PlanStep(domain=Domain.SEARCH, instruction="Search")
    plan = Plan(steps=[step])

    with pytest.raises(PlanningError, match="No CapabilityType mapping"):
        executor.execute(plan)


def test_executor_raises_on_execution_failure(
    mock_execution_service: MagicMock,
):
    # Make the execution service fail
    def side_effect(prompt: str, capability: CapabilityType) -> ProviderResult:
        return ProviderResult(success=False, error="API error")

    mock_execution_service.execute.side_effect = side_effect

    executor = PlanExecutor(execution_service=mock_execution_service)
    step = PlanStep(domain=Domain.CHAT, instruction="Hello")
    plan = Plan(steps=[step])

    with pytest.raises(PlanningError, match="Execution failed"):
        executor.execute(plan)


def test_executor_raises_on_empty_plan(
    mock_execution_service: MagicMock,
):
    executor = PlanExecutor(execution_service=mock_execution_service)
    plan = Plan(steps=[])

    with pytest.raises(PlanningError, match="empty Plan"):
        executor.execute(plan)