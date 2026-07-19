"""
===============================================================================
Tests for Planner
===============================================================================
"""
from __future__ import annotations
from unittest.mock import MagicMock
import pytest
import json

from hermes.planning.planner import Planner
from hermes.planning.domain import Domain
from hermes.planning.plan import Plan
from hermes.planning.exceptions import PlanningError
from hermes.planning.backend import PlanningBackend


@pytest.fixture
def mock_backend() -> MagicMock:
    mock = MagicMock(spec=PlanningBackend)
    mock.classify.return_value = "code"
    # By default, generate_plan will raise NotImplementedError to force fallback
    mock.generate_plan.side_effect = NotImplementedError("Not supported")
    return mock


def test_planner_returns_plan_with_domain(mock_backend):
    planner = Planner(mock_backend)
    plan = planner.plan("Write a Python function")

    assert isinstance(plan, Plan)
    assert len(plan.steps) == 1
    step = plan.steps[0]
    assert step.domain == Domain.CODE
    assert step.instruction == "Write a Python function"


def test_planner_uses_default_domain_on_unknown(mock_backend):
    mock_backend.classify.return_value = "unknown"
    planner = Planner(mock_backend, default_domain=Domain.CHAT)
    plan = planner.plan("Hello")

    assert plan.steps[0].domain == Domain.CHAT


def test_planner_raises_on_empty_prompt(mock_backend):
    planner = Planner(mock_backend)
    with pytest.raises(PlanningError, match="Prompt cannot be empty"):
        planner.plan("")


def test_planner_raises_on_backend_failure(mock_backend):
    # generate_plan raises NotImplementedError, so fallback to classify happens
    # Then classify raises PlanningError
    mock_backend.classify.side_effect = PlanningError("Backend error")
    planner = Planner(mock_backend)
    with pytest.raises(PlanningError, match="Backend error"):
        planner.plan("Test")


def test_planner_generates_multi_step_plan(mock_backend):
    # Override generate_plan to return valid JSON
    mock_backend.generate_plan = MagicMock()
    mock_backend.generate_plan.return_value = json.dumps([
        {"id": "step1", "domain": "search", "instruction": "Search for info"},
        {"id": "step2", "domain": "summarize", "instruction": "Summarize", "depends_on": ["step1"]}
    ])

    planner = Planner(mock_backend)
    plan = planner.plan("Search and summarize")

    assert len(plan.steps) == 2
    step1 = plan.steps[0]
    step2 = plan.steps[1]
    assert step1.domain == Domain.SEARCH
    assert step1.instruction == "Search for info"
    assert step2.domain == Domain.SUMMARIZE
    assert step2.instruction == "Summarize"
    assert step2.depends_on == ["step1"]
    assert step1.id == "step1"
    assert step2.id == "step2"


def test_planner_falls_back_on_not_implemented(mock_backend):
    # generate_plan already raises NotImplementedError by default
    mock_backend.classify.return_value = "chat"
    planner = Planner(mock_backend)
    plan = planner.plan("Say hello")
    assert len(plan.steps) == 1
    assert plan.steps[0].domain == Domain.CHAT


def test_planner_propagates_planning_error(mock_backend):
    # generate_plan raises a PlanningError (e.g., malformed JSON)
    mock_backend.generate_plan = MagicMock()
    mock_backend.generate_plan.side_effect = PlanningError("Generation error")

    planner = Planner(mock_backend)
    with pytest.raises(PlanningError, match="Generation error"):
        planner.plan("Test")


def test_planner_propagates_other_exceptions(mock_backend):
    # generate_plan raises an unexpected exception (e.g. ValueError)
    mock_backend.generate_plan = MagicMock()
    mock_backend.generate_plan.side_effect = ValueError("Unexpected error")

    planner = Planner(mock_backend)
    with pytest.raises(ValueError, match="Unexpected error"):
        planner.plan("Test")