"""
===============================================================================
Tests for Planning → Capability Adapter
===============================================================================
"""
from __future__ import annotations

import pytest

from hermes.capability.manager import CapabilityManager
from hermes.capability.resolver import CapabilityResolver
from hermes.capability.enums import CapabilityType
from hermes.planning.domain import Domain
from hermes.planning.plan import Plan, PlanStep
from hermes.planning.capability_adapter import PlanToExecutionPlanAdapter
from hermes.planning.exceptions import PlanningError


@pytest.fixture
def manager() -> CapabilityManager:
    return CapabilityManager()


@pytest.fixture
def resolver(manager: CapabilityManager) -> CapabilityResolver:
    # manager.registry is a public attribute
    return CapabilityResolver(manager.registry)


@pytest.fixture
def adapter(resolver: CapabilityResolver) -> PlanToExecutionPlanAdapter:
    return PlanToExecutionPlanAdapter(resolver=resolver)


def test_adapter_resolves_chat(adapter: PlanToExecutionPlanAdapter):
    step = PlanStep(domain=Domain.CHAT, instruction="Hello")
    plan = Plan(steps=[step])
    cap = adapter.resolve(plan)
    assert cap.name == CapabilityType.CHAT
    assert cap.enabled is True


def test_adapter_resolves_code(adapter: PlanToExecutionPlanAdapter):
    step = PlanStep(domain=Domain.CODE, instruction="Write code")
    plan = Plan(steps=[step])
    cap = adapter.resolve(plan)
    assert cap.name == CapabilityType.CODE


def test_adapter_resolves_reasoning(adapter: PlanToExecutionPlanAdapter):
    step = PlanStep(domain=Domain.REASONING, instruction="Reason")
    plan = Plan(steps=[step])
    cap = adapter.resolve(plan)
    assert cap.name == CapabilityType.REASONING


def test_adapter_resolves_search_as_web(adapter: PlanToExecutionPlanAdapter):
    step = PlanStep(domain=Domain.SEARCH, instruction="Search")
    plan = Plan(steps=[step])
    cap = adapter.resolve(plan)
    assert cap.name == CapabilityType.WEB


def test_adapter_resolves_summarize_as_chat(adapter: PlanToExecutionPlanAdapter):
    step = PlanStep(domain=Domain.SUMMARIZE, instruction="Summarize")
    plan = Plan(steps=[step])
    cap = adapter.resolve(plan)
    assert cap.name == CapabilityType.CHAT


def test_adapter_resolves_translate_as_chat(adapter: PlanToExecutionPlanAdapter):
    step = PlanStep(domain=Domain.TRANSLATE, instruction="Translate")
    plan = Plan(steps=[step])
    cap = adapter.resolve(plan)
    assert cap.name == CapabilityType.CHAT


def test_adapter_handles_unknown_domain(resolver: CapabilityResolver):
    # Use a custom mapping that explicitly removes SEARCH
    custom_mapping = {
        Domain.CHAT: CapabilityType.CHAT,
        Domain.CODE: CapabilityType.CODE,
        Domain.SEARCH: None,  # Explicitly remove mapping for SEARCH
    }
    # Create a new adapter with the custom mapping, using the injected resolver
    adapter_with_custom = PlanToExecutionPlanAdapter(resolver=resolver, mapping=custom_mapping)
    step = PlanStep(domain=Domain.SEARCH, instruction="Search")
    plan = Plan(steps=[step])
    with pytest.raises(PlanningError, match="No CapabilityType mapping"):
        adapter_with_custom.resolve(plan)


def test_adapter_raises_on_empty_plan(adapter: PlanToExecutionPlanAdapter):
    plan = Plan(steps=[])
    with pytest.raises(PlanningError, match="empty Plan"):
        adapter.resolve(plan)


def test_adapter_handles_multiple_steps(adapter: PlanToExecutionPlanAdapter):
    steps = [
        PlanStep(domain=Domain.CODE, instruction="Write code"),
        PlanStep(domain=Domain.SUMMARIZE, instruction="Summarize"),
    ]
    plan = Plan(steps=steps)
    cap = adapter.resolve(plan)
    # The first step's domain should determine the capability
    assert cap.name == CapabilityType.CODE