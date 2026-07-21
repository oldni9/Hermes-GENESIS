"""
===============================================================================
Tests for Agent Tool Runner
===============================================================================
"""

import pytest
from unittest.mock import MagicMock

from hermes.agent.executor.tool_runner import ToolRunner
from hermes.ai.adapters.provider_tool_adapter import ProviderToolAdapter
from hermes.ai.response import ToolCall, FunctionCall
from hermes.ai.tool import ToolManager, ToolResult, ToolStatus, ToolContext


@pytest.fixture
def mock_tool_manager():
    return MagicMock(spec=ToolManager)

@pytest.fixture
def tool_runner(mock_tool_manager):
    return ToolRunner(mock_tool_manager)

def make_provider_tool_call(call_id: str, name: str, args: any = {}):
    return ToolCall(id=call_id, type="function", function=FunctionCall(name=name, arguments=args))

def test_tool_runner_successful_execution(tool_runner, mock_tool_manager):
    tc1 = make_provider_tool_call("c1", "search", {"q": "hello"})
    tc2 = make_provider_tool_call("c2", "calc", {"x": 1})
    
    mock_tool_manager.execute_batch.return_value = [
        ToolResult(call_id="c1", status=ToolStatus.SUCCESS, output="Result 1"),
        ToolResult(call_id="c2", status=ToolStatus.SUCCESS, output="Result 2"),
    ]
    
    # FIX: Pass mock context
    results = tool_runner.execute([tc1, tc2], context=MagicMock(spec=ToolContext))
    
    assert len(results) == 2
    assert results["c1"].output == "Result 1"
    assert results["c2"].output == "Result 2"

def test_tool_runner_conversion_failure(tool_runner, mock_tool_manager):
    # Passing an integer as arguments triggers conversion failure in ProviderToolAdapter
    tc_bad = make_provider_tool_call("c1", "search", 123) 
    tc_good = make_provider_tool_call("c2", "calc", {})
    
    mock_tool_manager.execute_batch.return_value = [
        ToolResult(call_id="c2", status=ToolStatus.SUCCESS, output=42)
    ]
    
    # FIX: Pass mock context
    results = tool_runner.execute([tc_bad, tc_good], context=MagicMock(spec=ToolContext))
    
    assert len(results) == 2
    
    # The bad call should be mapped to a failed ToolResult
    assert results["c1"].status == ToolStatus.FAILED
    assert "Invalid arguments" in results["c1"].error
    
    # The good call should pass through
    assert results["c2"].output == 42

def test_tool_runner_missing_result(tool_runner, mock_tool_manager):
    tc1 = make_provider_tool_call("c1", "search")
    
    # Manager returns empty list (simulating a silent failure or mismatch)
    mock_tool_manager.execute_batch.return_value = []
    
    # FIX: Pass mock context
    results = tool_runner.execute([tc1], context=MagicMock(spec=ToolContext))
    
    assert len(results) == 1
    assert results["c1"].status == ToolStatus.FAILED
    assert "missing" in results["c1"].error