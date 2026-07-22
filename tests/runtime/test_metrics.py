"""
===============================================================================
Tests for RuntimeMetrics
===============================================================================
"""
from __future__ import annotations

import pytest
from unittest.mock import patch

from hermes.core.runtime import RuntimeMetrics, RuntimeClock


def test_metrics_defaults():
    metrics = RuntimeMetrics()
    assert metrics.used_prompt_tokens == 0
    assert metrics.used_completion_tokens == 0
    assert metrics.used_tokens == 0
    assert metrics.used_cost == 0.0
    assert metrics.tool_calls == 0
    assert metrics.llm_calls == 0
    assert metrics.finished_at is None

def test_metrics_accumulate_tokens():
    metrics = RuntimeMetrics()
    metrics.add_tokens(10, 20)
    metrics.add_tokens(5, 5)
    assert metrics.used_prompt_tokens == 15
    assert metrics.used_completion_tokens == 25
    assert metrics.used_tokens == 40

def test_metrics_accumulate_cost():
    metrics = RuntimeMetrics()
    metrics.add_cost(0.05)
    metrics.add_cost(0.10)
    assert metrics.used_cost == pytest.approx(0.15)

def test_metrics_counts():
    metrics = RuntimeMetrics()
    metrics.add_tool_call()
    metrics.add_tool_call()
    metrics.add_llm_call()
    assert metrics.tool_calls == 2
    assert metrics.llm_calls == 1

@patch('hermes.core.runtime.RuntimeClock.now')
def test_metrics_elapsed(mock_now):
    mock_now.return_value = 100.0
    metrics = RuntimeMetrics()
    metrics.start()
    
    mock_now.return_value = 105.5
    assert metrics.elapsed == 5.5
    
    mock_now.return_value = 110.0
    metrics.finish()
    assert metrics.finished_at == 110.0
    assert metrics.elapsed == 10.0
    assert metrics.elapsed >= 0  # Ensure no negative durations