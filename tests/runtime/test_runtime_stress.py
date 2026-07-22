"""
===============================================================================
Stress Tests for Runtime Limits
===============================================================================
"""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch

from hermes.core.runtime import RuntimeMetrics, RuntimePolicy, RuntimeContext, RuntimeClock
from hermes.core.errors import BudgetExceeded, DeadlineExceeded, ExecutionCancelled


def test_repeated_token_accumulation():
    metrics = RuntimeMetrics()
    
    ITERATIONS = 100
    TOKENS_PER_ITER = 10
    EXPECTED = ITERATIONS * TOKENS_PER_ITER
    
    for _ in range(ITERATIONS):
        metrics.add_tokens(TOKENS_PER_ITER // 2, TOKENS_PER_ITER // 2)
        
    assert metrics.used_tokens == EXPECTED

@patch('hermes.agent.executor.engine.RuntimeClock.now')
def test_budget_and_timeout_simultaneous(mock_now, execution_engine, mock_pipeline):
    from tests.conftest import make_text_response
    
    engine, trace, ctx = execution_engine
    mock_pipeline.execute.return_value = make_text_response("Hi", tokens=50)
    
    mock_now.return_value = 100.0
    ctx.metrics.start()  # Reset start time with mocked clock
    ctx.policy = RuntimePolicy(timeout=10.0, max_tokens=10) # Deadline 110.0
    
    # Advance time to breach deadline
    mock_now.return_value = 111.0
    
    config = MagicMock()
    config.engine_max_iterations = 1
    
    # Deadline should be checked first (based on code order in engine)
    with pytest.raises(DeadlineExceeded):
        engine.execute_turn(trace, 1, config=config)

def test_metrics_correct_after_failure(execution_engine, mock_pipeline):
    from tests.conftest import make_text_response
    
    engine, trace, ctx = execution_engine
    mock_pipeline.execute.return_value = make_text_response("Hi", tokens=50)
    
    ctx.policy = RuntimePolicy(max_tokens=10)
    ctx.metrics.start()
    
    config = MagicMock()
    config.engine_max_iterations = 1
    
    with pytest.raises(BudgetExceeded):
        engine.execute_turn(trace, 1, config=config)
        
    # Even though it failed, metrics should reflect the work done
    assert ctx.metrics.used_tokens == 50
    assert ctx.metrics.llm_calls == 1
    assert ctx.metrics.finished_at is None # Engine doesn't call finish(), executor does

def test_consecutive_policy_checks_no_corruption(execution_engine):
    """Ensure 100 consecutive checks don't mutate metrics unexpectedly."""
    engine, trace, ctx = execution_engine
    ctx.policy = RuntimePolicy(timeout=100.0, max_tokens=1000)
    
    # Add some initial state
    ctx.metrics.add_tokens(10, 10)
    initial_tokens = ctx.metrics.used_tokens
    initial_llm_calls = ctx.metrics.llm_calls
    initial_tool_calls = ctx.metrics.tool_calls
    
    # Run check_policy 100 times
    # Note: This will raise if it fails, so we catch it.
    # Since limits are high, it shouldn't fail.
    for i in range(100):
        engine._check_policy(trace, i)  # Removed config parameter
        
    # Metrics should be completely unchanged
    assert ctx.metrics.used_tokens == initial_tokens
    assert ctx.metrics.llm_calls == initial_llm_calls
    assert ctx.metrics.tool_calls == initial_tool_calls