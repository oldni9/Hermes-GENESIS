"""
===============================================================================
Tests for Planner
===============================================================================
"""

import pytest
from hermes.agent.planner.planner import DefaultPlanner
from hermes.agent.planner.decision import Decision, PlannerDecision
from hermes.agent.executor.state import ExecutionState, ExecutionStatus
from hermes.ai.conversation import AIConversation
from hermes.ai.response import AIResponse, ToolCall, FunctionCall, ResponseChoice, ResponseMessage


@pytest.fixture
def planner():
    return DefaultPlanner()

@pytest.fixture
def state():
    return ExecutionState(conversation=AIConversation())

def make_text_response(text: str = "Hello") -> AIResponse:
    return AIResponse(
        success=True,
        provider="test",
        model="test-model",
        choices=[ResponseChoice(index=0, message=ResponseMessage(role="assistant", content=text), finish_reason="stop")],
        result=text,
    )

def make_tool_response() -> AIResponse:
    tc = ToolCall(id="call_1", type="function", function=FunctionCall(name="test", arguments={}))
    return AIResponse(
        success=True,
        provider="test",
        model="test-model",
        choices=[ResponseChoice(index=0, message=ResponseMessage(role="assistant", content=""), finish_reason="tool_calls")],
        tool_calls=[tc],
    )

def make_error_response() -> AIResponse:
    return AIResponse(
        success=False,
        provider="test",
        model="test-model",
        message="API Error",
    )

def test_planner_finish(planner, state):
    """Test that the planner decides to FINISH when there are no tool calls."""
    response = make_text_response()
    decision = planner.decide(response, state)
    
    assert isinstance(decision, PlannerDecision)
    assert decision.decision == Decision.FINISH
    assert "final response" in decision.reason.lower()

def test_planner_call_tools(planner, state):
    """Test that the planner decides to CALL_TOOLS when tool calls are present."""
    response = make_tool_response()
    decision = planner.decide(response, state)
    
    assert decision.decision == Decision.CALL_TOOLS
    assert decision.metadata.get("tool_call_count") == 1

def test_planner_abort(planner, state):
    """Test that the planner decides to ABORT when the response is an error."""
    response = make_error_response()
    decision = planner.decide(response, state)
    
    assert decision.decision == Decision.ABORT
    assert "failed" in decision.reason.lower()
    assert decision.metadata.get("error") == "API Error"

def test_planner_is_pure(planner, state):
    """Test that the planner does not mutate the execution state."""
    response = make_tool_response()
    original_status = state.status
    original_iteration = state.iteration
    
    planner.decide(response, state)
    
    assert state.status == original_status
    assert state.iteration == original_iteration