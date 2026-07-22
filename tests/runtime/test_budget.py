"""
===============================================================================
Tests for Token Budget Enforcement
===============================================================================
"""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from hermes.agent.executor.trace import TraceEventType
from hermes.core.runtime import RuntimePolicy
from hermes.core.errors import BudgetExceeded


def test_budget_below_limit_passes(execution_engine, mock_pipeline):
    from tests.conftest import make_text_response
    
    engine, trace, ctx = execution_engine
    
    mock_pipeline.execute.return_value = make_text_response("Hi", tokens=50)
    ctx.policy = RuntimePolicy(max_tokens=100) # Below limit
    
    config = MagicMock()
    config.engine_max_iterations = 1
    
    response = engine.execute_turn(trace, 1, config=config)
    assert response.success

def test_budget_exact_boundary_passes(execution_engine, mock_pipeline):
    from tests.conftest import make_text_response
    
    engine, trace, ctx = execution_engine
    
    mock_pipeline.execute.return_value = make_text_response("Hi", tokens=100)
    ctx.policy = RuntimePolicy(max_tokens=100) # Exact limit
    
    config = MagicMock()
    config.engine_max_iterations = 1
    
    # Should complete successfully because used_tokens (100) <= max_tokens (100)
    response = engine.execute_turn(trace, 1, config=config)
    assert response.success

def test_budget_above_limit_fails(execution_engine, mock_pipeline):
    from tests.conftest import make_text_response
    
    engine, trace, ctx = execution_engine
    
    mock_pipeline.execute.return_value = make_text_response("Hi", tokens=101)
    ctx.policy = RuntimePolicy(max_tokens=100) # Above limit
    
    config = MagicMock()
    config.engine_max_iterations = 1
    
    with pytest.raises(BudgetExceeded):
        engine.execute_turn(trace, 1, config=config)
        
    events = [e.event_type for e in trace.events]
    assert TraceEventType.BUDGET_EXCEEDED in events