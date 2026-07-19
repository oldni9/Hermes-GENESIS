"""
===============================================================================
Tests for Agent Response
===============================================================================
"""
from __future__ import annotations

import pytest

from hermes.agent.response import AgentResponse


def test_agent_response_basic():
    resp = AgentResponse(success=True, text="test")
    assert resp.success is True
    assert resp.text == "test"
    assert resp.data is None
    assert resp.session is None
    assert resp.metadata == {}
    assert resp.plan is None
    assert resp.execution_graph is None


def test_agent_response_with_fields():
    resp = AgentResponse(
        success=False,
        text="error",
        data={"key": "value"},
        metadata={"meta": "data"},
    )
    assert resp.success is False
    assert resp.text == "error"
    assert resp.data == {"key": "value"}
    assert resp.metadata == {"meta": "data"}