"""
===============================================================================
Tests for AIPipeline with Orchestrator Integration

Verifies that:
    - Pipeline correctly delegates to orchestrator
    - Cache works with the pipeline
    - ExecutionPlan is created correctly

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from unittest.mock import MagicMock


from hermes.ai.cache import AICache
from hermes.ai.context import AIContext
from hermes.ai.orchestrator import AIOrchestrator
from hermes.ai.pipeline import AIPipeline
from hermes.ai.request import AIRequest
from hermes.ai.response import AIResponse


def test_pipeline_delegates_to_orchestrator():
    """Pipeline should pass the request to orchestrator."""
    orchestrator = MagicMock(spec=AIOrchestrator)
    orchestrator.execute.return_value = AIResponse(
        success=True,
        result="test response",
        provider="test",
    )

    pipeline = AIPipeline(orchestrator=orchestrator)

    request = AIRequest(prompt="hello", task="chat")
    context = AIContext()

    response = pipeline.execute(
        provider="test",
        request=request,
        context=context,
        use_cache=True,
        cache_ttl=60,
    )

    orchestrator.execute.assert_called_once()
    call_args = orchestrator.execute.call_args[1]
    assert call_args["request"] == request
    assert call_args["plan"].provider == "test"
    assert call_args["plan"].use_cache is True
    assert call_args["plan"].cache_ttl == 60
    assert response.success is True


def test_pipeline_cache_hit():
    """Pipeline should return cached response without calling orchestrator."""
    orchestrator = MagicMock(spec=AIOrchestrator)
    cache = MagicMock(spec=AICache)
    cache.get.return_value = AIResponse(
        success=True,
        result="cached response",
        provider="test",
    )

    pipeline = AIPipeline(orchestrator=orchestrator, cache=cache)

    request = AIRequest(prompt="hello", task="chat")
    context = AIContext()

    response = pipeline.execute(
        provider="test",
        request=request,
        context=context,
        use_cache=True,
    )

    cache.get.assert_called_once_with(request)
    orchestrator.execute.assert_not_called()
    assert response.result == "cached response"


def test_pipeline_cache_miss():
    """Pipeline should execute via orchestrator on cache miss."""
    orchestrator = MagicMock(spec=AIOrchestrator)
    orchestrator.execute.return_value = AIResponse(
        success=True,
        result="fresh response",
        provider="test",
    )

    cache = MagicMock(spec=AICache)
    cache.get.return_value = None

    pipeline = AIPipeline(orchestrator=orchestrator, cache=cache)

    request = AIRequest(prompt="hello", task="chat")
    context = AIContext()

    response = pipeline.execute(
        provider="test",
        request=request,
        context=context,
        use_cache=True,
        cache_ttl=60,
    )

    cache.get.assert_called_once_with(request)
    orchestrator.execute.assert_called_once()
    cache.store.assert_called_once()
    assert response.result == "fresh response"


def test_pipeline_cache_disabled():
    """Pipeline should skip cache when use_cache=False."""
    orchestrator = MagicMock(spec=AIOrchestrator)
    orchestrator.execute.return_value = AIResponse(
        success=True,
        result="fresh response",
        provider="test",
    )

    cache = MagicMock(spec=AICache)

    pipeline = AIPipeline(orchestrator=orchestrator, cache=cache)

    request = AIRequest(prompt="hello", task="chat")
    context = AIContext()

    response = pipeline.execute(
        provider="test",
        request=request,
        context=context,
        use_cache=False,
    )

    cache.get.assert_not_called()
    orchestrator.execute.assert_called_once()
    cache.store.assert_not_called()
    assert response.result == "fresh response"


def test_pipeline_execute_default():
    """Pipeline.execute_default should set request.task if missing."""
    orchestrator = MagicMock(spec=AIOrchestrator)
    orchestrator.execute.return_value = AIResponse(
        success=True,
        result="test response",
        provider="test",
    )

    pipeline = AIPipeline(orchestrator=orchestrator)

    request = AIRequest(prompt="hello")  # No task
    context = AIContext()

    response = pipeline.execute_default(
        capability="chat",
        request=request,
        context=context,
    )

    assert request.task == "chat"
    orchestrator.execute.assert_called_once()
