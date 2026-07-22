"""
===============================================================================
Tests for Runtime Trace Events & Payloads
===============================================================================
"""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from hermes.agent.executor.trace import TraceEventType
from hermes.core.runtime import RuntimePolicy


def test_trace_policy_check_payload(execution_engine, mock_pipeline):
    from tests.conftest import make_text_response
    
    engine, trace, ctx = execution_engine
    mock_pipeline.execute.return_value = make_text_response("Hi", tokens=10)
    
    TIMEOUT = 30.0
    MAX_TOKENS = 100
    
    ctx.policy = RuntimePolicy(timeout=TIMEOUT, max_tokens=MAX_TOKENS)
    
    config = MagicMock()
    config.engine_max_iterations = 1
    engine.execute_turn(trace, 1, config=config)
    
    check_events = [e for e in trace.events if e.event_type == TraceEventType.POLICY_CHECK]
    # Should be at least 2 checks: one before LLM, one after LLM
    assert len(check_events) >= 2
    
    # Validate schema exists on the first check
    payload = check_events[0].payload
    expected_keys = {
        "timeout_remaining",
        "tokens_remaining",
        "cancelled",
        "prompt_tokens",
        "completion_tokens",
        "tool_calls",
        "llm_calls",
        "elapsed",
        "budget_remaining"
    }
    assert set(payload.keys()) >= expected_keys
    
    # Validate the SECOND check (which occurs after the LLM call and has token usage)
    payload_after_llm = check_events[1].payload
    
    # Validate boundaries instead of exact values
    assert payload_after_llm["prompt_tokens"] == 5
    assert payload_after_llm["completion_tokens"] == 5
    assert payload_after_llm["budget_remaining"] > 0
    assert payload_after_llm["budget_remaining"] < MAX_TOKENS
    assert payload_after_llm["timeout_remaining"] is not None
    assert payload_after_llm["timeout_remaining"] <= TIMEOUT

def test_trace_policy_fail_payload(execution_engine, mock_pipeline):
    from tests.conftest import make_text_response
    
    engine, trace, ctx = execution_engine
    mock_pipeline.execute.return_value = make_text_response("Hi", tokens=102) # Use 102 to clearly exceed 100
    
    TOKEN_LIMIT = 100
    ctx.policy = RuntimePolicy(max_tokens=TOKEN_LIMIT)
    
    config = MagicMock()
    config.engine_max_iterations = 1
    
    try:
        engine.execute_turn(trace, 1, config=config)
    except Exception:
        pass # Expected to fail
        
    fail_events = [e for e in trace.events if e.event_type == TraceEventType.POLICY_FAIL]
    assert len(fail_events) == 1
    
    payload = fail_events[0].payload
    assert payload["reason"] == "budget_exceeded"