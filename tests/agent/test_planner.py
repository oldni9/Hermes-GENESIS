"""
===============================================================================
Tests for Reasoning Planner, Heuristics, Hasher, and Validator
===============================================================================
"""

import pytest
from hermes.agent.planner.reasoning_planner import ReasoningPlanner
from hermes.agent.planner.policy import PlannerPolicy
from hermes.agent.planner.confidence import HeuristicConfidenceEvaluator
from hermes.agent.planner.heuristics import (
    EmptyResponseRule, WeakAnswerRule, ToolCallRule, FinishRule, 
    RepeatedToolFailureRule, ToolAvailabilityRule
)
from hermes.agent.planner.decision import Decision, PlannerDecision
from hermes.agent.planner.hasher import ToolCallHasher
from hermes.agent.planner.tool_validation import ToolValidator, ToolValidationStatus
from hermes.agent.planner.telemetry import PlannerTraceEntry
from hermes.agent.executor.state import ExecutionState, ToolFailureRecord
from hermes.ai.conversation import AIConversation
from hermes.ai.response import AIResponse, ToolCall, FunctionCall, ResponseChoice, ResponseMessage
from hermes.ai.tool import ToolManager, ToolRegistry, Tool, ToolParameter, ParameterType, ToolStatus


@pytest.fixture
def policy():
    return PlannerPolicy(minimum_response_length=10, max_retries_on_failure=2)

@pytest.fixture
def evaluator():
    return HeuristicConfidenceEvaluator()

@pytest.fixture
def state():
    return ExecutionState(conversation=AIConversation())

@pytest.fixture
def tool_manager():
    tm = ToolManager(ToolRegistry())
    tm.register_function(name="search", func=lambda query: "result", description="Search")
    tm.register_function(name="disabled_tool", func=lambda: "ok", description="Disabled")
    tm.get_tool("disabled_tool").enabled = False
    return tm

@pytest.fixture
def validator(tool_manager):
    return ToolValidator(tool_manager.registry)

def make_text_response(text: str = "Hello") -> AIResponse:
    return AIResponse(
        success=True,
        provider="test",
        model="test-model",
        choices=[ResponseChoice(index=0, message=ResponseMessage(role="assistant", content=text), finish_reason="stop")],
        result=text,
    )

def make_tool_response(name: str = "search", args: any = {}, call_id: str = "call_1") -> AIResponse:
    tc = ToolCall(id=call_id, type="function", function=FunctionCall(name=name, arguments=args))
    return AIResponse(
        success=True,
        provider="test",
        model="test-model",
        choices=[ResponseChoice(index=0, message=ResponseMessage(role="assistant", content=""), finish_reason="tool_calls")],
        tool_calls=[tc],
    )

# --- ToolCallHasher Tests ---

def test_hasher_deterministic_dict_and_string():
    tc_dict = ToolCall(id="1", type="function", function=FunctionCall(name="search", arguments={"q": "test"}))
    tc_str = ToolCall(id="2", type="function", function=FunctionCall(name="search", arguments='{"q": "test"}'))
    assert ToolCallHasher.fingerprint(tc_dict) == ToolCallHasher.fingerprint(tc_str)

def test_hasher_different_arguments():
    tc1 = ToolCall(id="1", type="function", function=FunctionCall(name="search", arguments={"q": "A"}))
    tc2 = ToolCall(id="2", type="function", function=FunctionCall(name="search", arguments={"q": "B"}))
    assert ToolCallHasher.fingerprint(tc1) != ToolCallHasher.fingerprint(tc2)

# --- ToolValidator Tests ---

def test_validator_unknown_tool(validator):
    tc = ToolCall(id="1", type="function", function=FunctionCall(name="unknown", arguments={}))
    results = validator.validate_batch([tc])
    assert results[0].status == ToolValidationStatus.UNKNOWN_TOOL

def test_validator_disabled_tool(validator):
    tc = ToolCall(id="1", type="function", function=FunctionCall(name="disabled_tool", arguments={}))
    results = validator.validate_batch([tc])
    assert results[0].status == ToolValidationStatus.DISABLED_TOOL

def test_validator_malformed_arguments(validator):
    tc = ToolCall(id="1", type="function", function=FunctionCall(name="search", arguments=123))
    results = validator.validate_batch([tc])
    assert results[0].status == ToolValidationStatus.MALFORMED_ARGUMENTS

def test_validator_valid_tool(validator):
    tc = ToolCall(id="1", type="function", function=FunctionCall(name="search", arguments={"q": "test"}))
    results = validator.validate_batch([tc])
    assert results[0].status == ToolValidationStatus.VALID

# --- Rule Tests ---

def test_tool_availability_rule_aborts_unknown_tool(state, policy, validator):
    rule = ToolAvailabilityRule(validator)
    response = make_tool_response(name="unknown_tool")
    decision = rule.evaluate(response, state, policy)
    assert decision is not None
    assert decision.decision == Decision.ABORT
    assert "not registered" in decision.reason

def test_tool_availability_rule_retries_malformed_args(state, policy, validator):
    rule = ToolAvailabilityRule(validator)
    response = AIResponse(
        success=True,
        provider="test",
        model="test-model",
        choices=[ResponseChoice(index=0, message=ResponseMessage(role="assistant", content=""), finish_reason="tool_calls")],
        tool_calls=[ToolCall(id="1", type="function", function=FunctionCall(name="search", arguments=123))]
    )
    decision = rule.evaluate(response, state, policy)
    assert decision is not None
    assert decision.decision == Decision.RETRY
    assert "validation" in decision.feedback

def test_repeated_tool_failure_rule_aborts(state, policy):
    rule = RepeatedToolFailureRule()
    response = make_tool_response(name="search", args={"q": "test"})
    fingerprint = ToolCallHasher.fingerprint(response.tool_calls[0])
    state.failure_history.append(ToolFailureRecord(
        fingerprint=fingerprint,
        tool_name="search",
        error="API Error",
        iteration=1
    ))
    decision = rule.evaluate(response, state, policy)
    assert decision is not None
    assert decision.decision == Decision.ABORT
    assert "Repeated failure" in decision.reason

def test_repeated_tool_failure_rule_allows_new_args(state, policy):
    rule = RepeatedToolFailureRule()
    response = make_tool_response(name="search", args={"q": "new_query"})
    state.failure_history.append(ToolFailureRecord(
        fingerprint="different_hash",
        tool_name="search",
        error="API Error",
        iteration=1
    ))
    decision = rule.evaluate(response, state, policy)
    assert decision is None

# --- ReasoningPlanner Integration & Telemetry Tests ---

def test_reasoning_planner_records_telemetry(state, tool_manager):
    planner = ReasoningPlanner(registry=tool_manager.registry)
    
    resp_tools = make_tool_response(name="search", args={"q": "test"})
    dec = planner.decide(resp_tools, state)
    assert dec.decision == Decision.CALL_TOOLS
    
    assert len(state.planner_trace) > 0
    last_trace = state.planner_trace[-1]
    assert isinstance(last_trace, PlannerTraceEntry)
    assert last_trace.matched is True
    assert last_trace.decision == Decision.CALL_TOOLS
    assert last_trace.rule_name == "ToolCallRule"
    
    resp_unknown = make_tool_response(name="unknown")
    dec = planner.decide(resp_unknown, state)
    assert dec.decision == Decision.ABORT
    last_trace = state.planner_trace[-1]
    assert last_trace.decision == Decision.ABORT
    assert last_trace.rule_name == "ToolAvailabilityRule"