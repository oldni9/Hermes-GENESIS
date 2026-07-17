"""
===============================================================================
Tests for Hermes AI Middleware

Verifies:
    - MiddlewareContext
    - BaseMiddleware (with concrete implementations)
    - MiddlewareChain execution order
    - Short‑circuit behaviour
    - Integration with AIPipeline
===============================================================================
"""

from __future__ import annotations

from unittest.mock import MagicMock, create_autospec

import pytest

from hermes.ai.context import AIContext
from hermes.ai.middleware import (
    BaseMiddleware,
    MiddlewareChain,
    MiddlewareContext,
    MiddlewareShortCircuit,
)
from hermes.ai.pipeline import AIPipeline
from hermes.ai.request import AIRequest
from hermes.ai.response import AIResponse


# ------------------------------------------------------------------
# Concrete Middleware for testing
# ------------------------------------------------------------------

class LoggingMiddleware(BaseMiddleware):
    """Records calls for verification."""
    def __init__(self):
        self.before_calls = []
        self.after_calls = []

    def before(self, ctx: MiddlewareContext) -> None:
        self.before_calls.append((ctx.request.prompt, ctx.metadata.get("key")))
        ctx.metadata["before_logged"] = True

    def after(self, ctx: MiddlewareContext) -> None:
        self.after_calls.append((ctx.response.text(), ctx.metadata.get("key")))
        ctx.metadata["after_logged"] = True


class ModifyingMiddleware(BaseMiddleware):
    """Modifies the request and response."""
    def before(self, ctx: MiddlewareContext) -> None:
        ctx.request.prompt = "modified: " + ctx.request.prompt
        ctx.metadata["modified_before"] = True

    def after(self, ctx: MiddlewareContext) -> None:
        ctx.response = AIResponse(
            success=True,
            result="modified: " + ctx.response.text(),
            provider=ctx.response.provider,
            model=ctx.response.model,
        )
        ctx.metadata["modified_after"] = True


class ShortCircuitMiddleware(BaseMiddleware):
    """Short‑circuits the chain and sets a response."""
    def before(self, ctx: MiddlewareContext) -> None:
        ctx.response = AIResponse(
            success=True,
            result="short‑circuited response",
            provider="short",
            model="short",
        )
        ctx.short_circuit = True

    def after(self, ctx: MiddlewareContext) -> None:
        pass  # never called


class ErrorMiddleware(BaseMiddleware):
    """Raises an exception."""
    def before(self, ctx: MiddlewareContext) -> None:
        raise ValueError("before error")

    def after(self, ctx: MiddlewareContext) -> None:
        raise ValueError("after error")


# ------------------------------------------------------------------
# Test MiddlewareContext
# ------------------------------------------------------------------

def test_middleware_context() -> None:
    request = AIRequest(prompt="test")
    context = AIContext()
    ctx = MiddlewareContext(request=request, context=context, metadata={"k": "v"})
    assert ctx.request is request
    assert ctx.context is context
    assert ctx.metadata["k"] == "v"
    assert ctx.short_circuit is False
    assert ctx.response is None


# ------------------------------------------------------------------
# Test MiddlewareChain
# ------------------------------------------------------------------

def test_chain_executes_before_in_order() -> None:
    mw1 = LoggingMiddleware()
    mw2 = LoggingMiddleware()
    chain = MiddlewareChain([mw1, mw2])
    request = AIRequest(prompt="hello")
    ctx = MiddlewareContext(request=request)

    chain.execute_before(ctx)

    assert len(mw1.before_calls) == 1
    assert len(mw2.before_calls) == 1
    assert mw1.before_calls[0][0] == "hello"
    assert mw2.before_calls[0][0] == "hello"


def test_chain_executes_after_in_reverse_order() -> None:
    mw1 = LoggingMiddleware()
    mw2 = LoggingMiddleware()
    chain = MiddlewareChain([mw1, mw2])
    response = AIResponse(success=True, result="hi")
    ctx = MiddlewareContext(request=AIRequest(prompt=""), response=response)

    chain.execute_after(ctx)

    assert len(mw1.after_calls) == 1
    assert len(mw2.after_calls) == 1
    # After hooks are called in reverse order
    assert mw2.after_calls[0][0] == "hi"
    assert mw1.after_calls[0][0] == "hi"


def test_chain_short_circuit() -> None:
    mw1 = ShortCircuitMiddleware()
    mw2 = LoggingMiddleware()
    chain = MiddlewareChain([mw1, mw2])
    ctx = MiddlewareContext(request=AIRequest(prompt=""))

    with pytest.raises(MiddlewareShortCircuit):
        chain.execute_before(ctx)

    # mw2.before should NOT have been called
    assert len(mw2.before_calls) == 0


def test_chain_propagates_exception() -> None:
    mw = ErrorMiddleware()
    chain = MiddlewareChain([mw])
    ctx = MiddlewareContext(request=AIRequest(prompt=""))

    with pytest.raises(ValueError, match="before error"):
        chain.execute_before(ctx)


# ------------------------------------------------------------------
# Integration with AIPipeline
# ------------------------------------------------------------------

@pytest.fixture
def mock_orchestrator() -> MagicMock:
    orch = MagicMock()
    orch.execute.return_value = AIResponse(
        success=True,
        result="orchestrator response",
        provider="test",
        model="test",
    )
    return orch


def test_pipeline_without_middleware(mock_orchestrator: MagicMock) -> None:
    """Pipeline behaves as before when no middleware is given."""
    pipeline = AIPipeline(orchestrator=mock_orchestrator)
    request = AIRequest(prompt="hello")
    response = pipeline.execute(provider="test", request=request)

    mock_orchestrator.execute.assert_called_once()
    assert response.result == "orchestrator response"


def test_pipeline_with_middleware(mock_orchestrator: MagicMock) -> None:
    """Middleware is executed before and after."""
    mw = LoggingMiddleware()
    pipeline = AIPipeline(orchestrator=mock_orchestrator, middlewares=[mw])
    request = AIRequest(prompt="hello")
    response = pipeline.execute(provider="test", request=request)

    # before called
    assert len(mw.before_calls) == 1
    assert mw.before_calls[0][0] == "hello"
    # after called
    assert len(mw.after_calls) == 1
    assert mw.after_calls[0][0] == "orchestrator response"

    mock_orchestrator.execute.assert_called_once()


def test_pipeline_middleware_modifies_request(mock_orchestrator: MagicMock) -> None:
    """Middleware can modify the request before orchestration."""
    mw = ModifyingMiddleware()
    pipeline = AIPipeline(orchestrator=mock_orchestrator, middlewares=[mw])
    request = AIRequest(prompt="hello")
    pipeline.execute(provider="test", request=request)

    # Orchestrator should receive the modified request
    call_request = mock_orchestrator.execute.call_args[1]["request"]
    assert call_request.prompt == "modified: hello"


def test_pipeline_middleware_modifies_response(mock_orchestrator: MagicMock) -> None:
    """Middleware can modify the response after orchestration."""
    mw = ModifyingMiddleware()
    pipeline = AIPipeline(orchestrator=mock_orchestrator, middlewares=[mw])
    request = AIRequest(prompt="hello")
    response = pipeline.execute(provider="test", request=request)

    assert response.result == "modified: orchestrator response"


def test_pipeline_short_circuit(mock_orchestrator: MagicMock) -> None:
    """Middleware can short‑circuit and skip the orchestrator."""
    mw = ShortCircuitMiddleware()
    pipeline = AIPipeline(orchestrator=mock_orchestrator, middlewares=[mw])
    request = AIRequest(prompt="hello")
    response = pipeline.execute(provider="test", request=request)

    mock_orchestrator.execute.assert_not_called()
    assert response.result == "short‑circuited response"


def test_pipeline_short_circuit_without_response_raises_error(
    mock_orchestrator: MagicMock,
) -> None:
    """If a middleware short‑circuits without setting a response, raise an error."""

    class BadMiddleware(BaseMiddleware):
        def before(self, ctx: MiddlewareContext) -> None:
            ctx.short_circuit = True
        def after(self, ctx: MiddlewareContext) -> None:
            pass

    pipeline = AIPipeline(orchestrator=mock_orchestrator, middlewares=[BadMiddleware()])
    request = AIRequest(prompt="hello")
    with pytest.raises(RuntimeError, match="short‑circuited but no response was set"):
        pipeline.execute(provider="test", request=request)


def test_pipeline_middleware_error_before(mock_orchestrator: MagicMock) -> None:
    """Error in before middleware propagates."""
    mw = ErrorMiddleware()
    pipeline = AIPipeline(orchestrator=mock_orchestrator, middlewares=[mw])
    request = AIRequest(prompt="hello")
    with pytest.raises(ValueError, match="before error"):
        pipeline.execute(provider="test", request=request)


def test_pipeline_middleware_error_after(mock_orchestrator: MagicMock) -> None:
    """Error in after middleware propagates."""

    class ErrorAfterMiddleware(BaseMiddleware):
        def before(self, ctx: MiddlewareContext) -> None:
            pass
        def after(self, ctx: MiddlewareContext) -> None:
            raise ValueError("after error")

    pipeline = AIPipeline(orchestrator=mock_orchestrator, middlewares=[ErrorAfterMiddleware()])
    request = AIRequest(prompt="hello")
    with pytest.raises(ValueError, match="after error"):
        pipeline.execute(provider="test", request=request)


def test_pipeline_cache_still_works_with_middleware(mock_orchestrator: MagicMock) -> None:
    """Cache is checked before middleware and stored after middleware."""
    from hermes.ai.cache import AICache
    cache = MagicMock(spec=AICache)
    cache.get.return_value = None  # miss

    pipeline = AIPipeline(orchestrator=mock_orchestrator, cache=cache, middlewares=[LoggingMiddleware()])
    request = AIRequest(prompt="hello")
    pipeline.execute(provider="test", request=request, use_cache=True)

    cache.get.assert_called_once()
    cache.store.assert_called_once()


def test_pipeline_cache_hit_skips_middleware(mock_orchestrator: MagicMock) -> None:
    """If cache hit, middleware is NOT executed."""
    from hermes.ai.cache import AICache
    cached_response = AIResponse(success=True, result="cached", provider="test", model="test")
    cache = MagicMock(spec=AICache)
    cache.get.return_value = cached_response

    mw = LoggingMiddleware()
    pipeline = AIPipeline(orchestrator=mock_orchestrator, cache=cache, middlewares=[mw])
    request = AIRequest(prompt="hello")
    response = pipeline.execute(provider="test", request=request, use_cache=True)

    assert response is cached_response
    assert len(mw.before_calls) == 0
    assert len(mw.after_calls) == 0
    mock_orchestrator.execute.assert_not_called()