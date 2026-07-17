"""
===============================================================================
Tests for Execution Contracts

Verifies that the contract types can be instantiated, have expected fields,
and satisfy the protocols when used with dummy implementations.

No network.
No providers.
No API keys.
Only contract validation.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest

from hermes.execution import (
    ExecutionContext,
    ExecutionEngine,
    ExecutionLifecycle,
    ExecutionRequest,
)


@dataclass(slots=True)
class DummyRequest:
    """Minimal implementation of ExecutionRequest for testing."""

    prompt: str
    provider: str | None = None
    model: str | None = None
    options: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


class DummyEngine:
    """Minimal implementation of ExecutionEngine for protocol testing."""

    def start(self) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def is_ready(self) -> bool:
        return True

    def execute(self, request: ExecutionRequest, context: ExecutionContext | None = None) -> dict[str, Any]:
        return {"success": True, "result": f"executed: {request.prompt}"}


def test_execution_context():
    ctx = ExecutionContext(session_id="sess-1", priority=10)
    assert ctx.session_id == "sess-1"
    assert ctx.priority == 10


def test_execution_request_protocol():
    req = DummyRequest(prompt="hello")
    assert req.prompt == "hello"
    assert req.provider is None
    assert req.model is None


def test_dummy_engine_protocol():
    engine = DummyEngine()
    assert isinstance(engine, ExecutionEngine)
    assert isinstance(engine, ExecutionLifecycle)

    req = DummyRequest(prompt="test")
    result = engine.execute(req)
    assert result["success"] is True
    assert "test" in result["result"]