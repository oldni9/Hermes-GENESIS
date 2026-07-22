"""
===============================================================================
Tests for CancellationToken & Enforcement
===============================================================================
"""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from hermes.agent.executor.trace import TraceEventType
from hermes.core.runtime import RuntimePolicy, CancellationToken
from hermes.core.errors import ExecutionCancelled


def test_token_cancel():
    token = CancellationToken()
    assert not token.cancelled
    token.cancel()
    assert token.cancelled

def test_cancellation_before_run(execution_engine):
    engine, trace, ctx = execution_engine
    ctx.policy = RuntimePolicy()
    ctx.cancellation_token.cancel()
    
    # Should raise before hitting the pipeline
    with pytest.raises(ExecutionCancelled):
        engine.execute_turn(trace, 1, config=MagicMock())
        
    events = [e.event_type for e in trace.events]
    assert TraceEventType.CANCELLED in events

def test_cancellation_during_tool_execution(execution_engine, mock_pipeline, tool_manager):
    from hermes.ai.response import AIResponse, ToolCall, FunctionCall
    from tests.conftest import make_text_response
    
    engine, trace, ctx = execution_engine
    
    # Simulate LLM returning a tool call
    tc = ToolCall(id="1", type="function", function=FunctionCall(name="dummy", arguments={}))
    tool_resp = AIResponse(success=True, provider="test", model="test", tool_calls=[tc])
    
    # Use a single function for side_effect so it actually gets called by the mock
    def pipeline_side_effect(*args, **kwargs):
        if not ctx.cancellation_token.cancelled:
            ctx.cancellation_token.cancel()
            return tool_resp
        return make_text_response("Done")
        
    mock_pipeline.execute.side_effect = pipeline_side_effect
    
    # Register a dummy tool so ToolRunner doesn't fail
    tool_manager.register_function(name="dummy", func=lambda: "ok")
    
    config = MagicMock()
    config.engine_max_iterations = 5
    
    # Should halt on the next policy check (which happens after tool execution)
    with pytest.raises(ExecutionCancelled):
        engine.execute_turn(trace, 1, config=config)
        
    # Strengthened Assertions: Prove the loop was interrupted
    # 1. The pipeline was called exactly once (for the tool response).
    # The second LLM call should NEVER happen.
    assert mock_pipeline.execute.call_count == 1
    
    # 2. Verify execution started but was interrupted via trace events
    events = [e.event_type for e in trace.events]
    assert TraceEventType.POLICY_FAIL in events
    assert TraceEventType.CANCELLED in events