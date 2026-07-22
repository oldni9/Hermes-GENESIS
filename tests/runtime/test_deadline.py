"""
===============================================================================
Tests for Deadline (Timeout) Enforcement
===============================================================================
"""
from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock

from hermes.agent.executor.trace import TraceEventType
from hermes.core.runtime import RuntimePolicy
from hermes.core.errors import DeadlineExceeded


@patch('hermes.agent.executor.engine.RuntimeClock.now')
def test_deadline_exceeded(mock_now, execution_engine):
    engine, trace, ctx = execution_engine
    
    mock_now.return_value = 100.0
    ctx.metrics.start()  # Reset start time with mocked clock
    ctx.policy = RuntimePolicy(timeout=10.0) # Deadline is 110.0
    
    # Time passes -> 111.0 (exceeded)
    mock_now.return_value = 111.0
    
    with pytest.raises(DeadlineExceeded):
        engine.execute_turn(trace, 1, config=MagicMock())
        
    events = [e.event_type for e in trace.events]
    assert TraceEventType.DEADLINE_EXCEEDED in events

@patch('hermes.agent.executor.engine.RuntimeClock.now')
def test_deadline_exact_boundary_pass(mock_now, execution_engine, mock_pipeline):
    from tests.conftest import make_text_response
    engine, trace, ctx = execution_engine
    
    mock_pipeline.execute.return_value = make_text_response("Hi")
    
    mock_now.return_value = 100.0
    ctx.metrics.start()  # Reset start time with mocked clock
    ctx.policy = RuntimePolicy(timeout=10.0) # Deadline is 110.0
    
    # Time passes -> 109.9 (should pass because check is `remaining <= 0.0`)
    mock_now.return_value = 109.9
    
    # Should complete successfully
    config = MagicMock()
    config.engine_max_iterations = 1
    response = engine.execute_turn(trace, 1, config=config)
    
    assert response.success