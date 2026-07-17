"""
===============================================================================
Tests for AI Orchestrator Layer

Unit tests for:
    - ExecutionPlan
    - RetryPolicy
    - ProviderSelector
    - ResponseProcessor
    - AIOrchestrator

No network calls.
Mock providers using the real API.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

import time
from typing import Any
from unittest.mock import MagicMock

import pytest

from hermes.ai.metadata import AIMetadata
from hermes.ai.orchestrator import (
    AIOrchestrator,
    ExecutionPlan,
    ProviderSelector,
    ResponseProcessor,
    RetryPolicy,
)
from hermes.ai.orchestrator.exceptions import (
    ValidationError,
    ProviderSelectionError,
    RetryExhaustedError,
)
from hermes.ai.provider import BaseAIProvider
from hermes.ai.registry import AIRegistry
from hermes.ai.request import AIRequest
from hermes.ai.response import AIResponse
from hermes.core.exceptions import ProviderError


# ------------------------------------------------------------------
# Real Mock Provider (matches actual BaseAIProvider API)
# ------------------------------------------------------------------

class MockProvider(BaseAIProvider):
    """Mock provider that implements the real BaseAIProvider interface."""

    def __init__(self, name: str = "mock", supports: bool = True):
        super().__init__()
        self._name = name
        self._supports = supports
        self._metadata = AIMetadata(
            name=name,
            provider=name,
            capabilities=["chat", "generate"] if supports else [],
            enabled=True,
        )

    @property
    def metadata(self) -> AIMetadata:
        return self._metadata

    def execute(self, request: AIRequest, context: Any = None) -> AIResponse:
        return AIResponse(
            success=True,
            result=f"Mock response: {request.prompt}",
            provider=self._name,
            model=request.model or "mock-model",
        )


# ------------------------------------------------------------------
# ExecutionPlan Tests
# ------------------------------------------------------------------

def test_execution_plan_defaults():
    plan = ExecutionPlan()
    assert plan.provider is None
    assert plan.model is None
    assert plan.temperature == 0.7
    assert plan.max_tokens == 4096
    assert plan.timeout == 60.0
    assert plan.retry_attempts == 3
    assert plan.use_cache is True
    assert plan.cache_ttl is None


def test_execution_plan_with_options():
    plan = ExecutionPlan(provider="test", model="test-model")
    new_plan = plan.with_options(temperature=0.9, max_tokens=8192)
    assert new_plan.provider == "test"
    assert new_plan.model == "test-model"
    assert new_plan.temperature == 0.9
    assert new_plan.max_tokens == 8192
    # Original unchanged
    assert plan.temperature == 0.7


def test_execution_plan_to_dict():
    plan = ExecutionPlan(provider="test", use_cache=False)
    d = plan.to_dict()
    assert d["provider"] == "test"
    assert d["use_cache"] is False


# ------------------------------------------------------------------
# RetryPolicy Tests
# ------------------------------------------------------------------

def test_retry_policy_success():
    policy = RetryPolicy(max_attempts=3)
    called = 0

    def func():
        nonlocal called
        called += 1
        return "success"

    result, attempts, elapsed = policy.execute(func)
    assert result == "success"
    assert attempts == 1
    assert called == 1


def test_retry_policy_retry():
    policy = RetryPolicy(max_attempts=3, initial_delay=0.01, max_delay=0.1)
    called = 0

    def func():
        nonlocal called
        called += 1
        if called < 3:
            raise ValueError("temporary")
        return "success"

    result, attempts, elapsed = policy.execute(func)
    assert result == "success"
    assert attempts == 3
    assert called == 3


def test_retry_policy_exhausted():
    policy = RetryPolicy(max_attempts=2, initial_delay=0.01)

    def func():
        raise ValueError("always fails")

    with pytest.raises(RetryExhaustedError) as exc_info:
        policy.execute(func)
    assert "always fails" in str(exc_info.value)


def test_retry_policy_non_retryable():
    policy = RetryPolicy(
        max_attempts=3,
        retryable_exceptions=(TimeoutError,),
    )

    def func():
        raise ValueError("not retryable")

    with pytest.raises(ValueError):
        policy.execute(func)


def test_retry_policy_should_retry():
    policy = RetryPolicy(
        max_attempts=3,
        should_retry=lambda e: "retry" in str(e),
    )

    def func():
        raise ValueError("retry this")

    with pytest.raises(RetryExhaustedError) as exc_info:
        policy.execute(func)
    assert "retry this" in str(exc_info.value)


# ------------------------------------------------------------------
# ProviderSelector Tests
# ------------------------------------------------------------------

def test_provider_selector_select():
    registry = AIRegistry()
    provider = MockProvider("test")
    registry.register(provider)

    selector = ProviderSelector(registry)
    request = AIRequest(prompt="hello", task="chat")

    selected_provider, model = selector.select(request)
    assert selected_provider.name == "test"
    assert model is None


def test_provider_selector_explicit_provider():
    registry = AIRegistry()
    registry.register(MockProvider("provider1"))
    registry.register(MockProvider("provider2"))

    selector = ProviderSelector(registry)
    request = AIRequest(prompt="hello")

    provider, model = selector.select(request, preferred_provider="provider2")
    assert provider.name == "provider2"


def test_provider_selector_explicit_model():
    registry = AIRegistry()
    registry.register(MockProvider("test"))

    selector = ProviderSelector(registry)
    request = AIRequest(prompt="hello", model="custom-model")

    provider, model = selector.select(request)
    assert provider.name == "test"
    assert model == "custom-model"


def test_provider_selector_no_provider():
    registry = AIRegistry()
    selector = ProviderSelector(registry)
    request = AIRequest(prompt="hello", task="chat")

    with pytest.raises(ProviderSelectionError):
        selector.select(request)


def test_provider_selector_preferred_not_found():
    registry = AIRegistry()
    registry.register(MockProvider("test"))

    selector = ProviderSelector(registry)
    request = AIRequest(prompt="hello")

    with pytest.raises(ProviderSelectionError):
        selector.select(request, preferred_provider="nonexistent")


# ------------------------------------------------------------------
# ResponseProcessor Tests
# ------------------------------------------------------------------

def test_response_processor_process():
    processor = ResponseProcessor()
    response = AIResponse(
        success=True,
        message="hello",
        result="hello",
        provider="",
        model="",
    )
    start = time.time()

    processed = processor.process(
        raw_response=response,
        provider_name="test_provider",
        model_name="test_model",
        start_time=start,
    )

    assert processed.provider == "test_provider"
    assert processed.model == "test_model"
    assert processed.metadata["provider"] == "test_provider"
    assert processed.metadata["model"] == "test_model"
    # Check either duration or metadata duration
    duration = processed.duration if processed.duration > 0 else processed.metadata.get("duration", 0)
    assert duration > 0


def test_response_processor_error():
    processor = ResponseProcessor()
    error_response = processor.create_error_response(
        error="Something went wrong",
        provider_name="test_provider",
        model_name="test_model",
        status_code=500,
    )

    assert error_response.success is False
    assert error_response.message == "Something went wrong"
    assert error_response.provider == "test_provider"
    assert error_response.model == "test_model"
    assert error_response.metadata["status_code"] == 500


# ------------------------------------------------------------------
# AIOrchestrator Tests
# ------------------------------------------------------------------

def test_orchestrator_execute():
    registry = AIRegistry()
    provider = MockProvider("test")
    registry.register(provider)

    selector = ProviderSelector(registry)
    processor = ResponseProcessor()
    retry_policy = RetryPolicy(max_attempts=1)

    orchestrator = AIOrchestrator(
        manager=MagicMock(),
        provider_selector=selector,
        response_processor=processor,
        retry_policy=retry_policy,
    )

    def mock_execute(provider_name, request, context=None):
        return AIResponse(
            success=True,
            result=f"Mock response: {request.prompt}",
            provider=provider_name,
            model=request.model or "mock-model",
        )

    orchestrator._manager.execute = mock_execute

    request = AIRequest(prompt="hello", task="chat")
    plan = ExecutionPlan(provider="test")

    response = orchestrator.execute(request, plan)

    assert response.success is True
    assert "Mock response: hello" in response.result


def test_orchestrator_validation():
    registry = AIRegistry()
    selector = ProviderSelector(registry)
    processor = ResponseProcessor()

    orchestrator = AIOrchestrator(
        manager=MagicMock(),
        provider_selector=selector,
        response_processor=processor,
    )

    request = AIRequest(prompt="", input=None, task="chat")
    plan = ExecutionPlan()

    with pytest.raises(ValidationError):
        orchestrator.execute(request, plan)


def test_orchestrator_provider_error():
    registry = AIRegistry()
    provider = MockProvider("test")
    registry.register(provider)

    selector = ProviderSelector(registry)
    processor = ResponseProcessor()

    manager = MagicMock()
    manager.execute.side_effect = ProviderError("API key expired")

    orchestrator = AIOrchestrator(
        manager=manager,
        provider_selector=selector,
        response_processor=processor,
        retry_policy=RetryPolicy(max_attempts=1),
    )

    request = AIRequest(prompt="hello", task="chat")
    plan = ExecutionPlan(provider="test")

    response = orchestrator.execute(request, plan)
    assert response.success is False
    assert "API key expired" in response.message


def test_orchestrator_unexpected_error():
    registry = AIRegistry()
    provider = MockProvider("test")
    registry.register(provider)

    selector = ProviderSelector(registry)
    processor = ResponseProcessor()

    manager = MagicMock()
    manager.execute.side_effect = AttributeError("non-existent method")

    # Use a retry policy that does NOT retry AttributeError
    policy = RetryPolicy(
        max_attempts=1,
        retryable_exceptions=(TimeoutError,),
    )

    orchestrator = AIOrchestrator(
        manager=manager,
        provider_selector=selector,
        response_processor=processor,
        retry_policy=policy,
    )

    request = AIRequest(prompt="hello", task="chat")
    plan = ExecutionPlan(provider="test")

    # AttributeError is NOT retryable, so it should be raised directly
    with pytest.raises(AttributeError):
        orchestrator.execute(request, plan)