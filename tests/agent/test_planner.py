"""
===============================================================================
Tests for Reasoning Planner & Heuristics
===============================================================================
"""

import pytest
from hermes.agent.planner.reasoning_planner import ReasoningPlanner
from hermes.agent.planner.policy import PlannerPolicy
from hermes.agent.planner.confidence import HeuristicConfidenceEvaluator
from hermes.agent.planner.heuristics import (
    EmptyResponseRule, WeakAnswerRule, ToolCallRule, FinishRule, RepeatedToolFailureRule
)
from hermes.agent.planner.decision import Decision, PlannerDecision
from hermes.agent.executor.state import ExecutionState
from hermes.ai.conversation import AIConversation
from hermes.ai.response import AIResponse, ToolCall, FunctionCall, ResponseChoice, ResponseMessage
from hermes.ai.tool import ToolResult, ToolStatus


@pytest.fixture
def policy():
    return PlannerPolicy(minimum_response_length=10, max_retries_on_failure=2)

@pytest.fixture
def evaluator():
    return HeuristicConfidenceEvaluator()

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
    return AIResponse(success=False, provider="test", model="test-model", message="API Error")

def test_empty_response_rule_retries(state, policy):
    rule = EmptyResponseRule()
    response = make_text_response("") # Empty
    
    decision = rule.evaluate(response, state, policy)
    assert decision is not None
    assert decision.decision == Decision.RETRY
    # FIX: Assert against the actual feedback string
    assert "empty" in decision.feedback.lower()

def test_empty_response_rule_aborts_on_max_retries(state, policy):
    rule = EmptyResponseRule()
    response = make_text_response("")
    state.retry_count = 2 # Max retries reached
    
    decision = rule.evaluate(response, state, policy)
    assert decision is not None
    assert decision.decision == Decision.ABORT

def test_weak_answer_rule_retries_on_short_length(state, policy, evaluator):
    rule = WeakAnswerRule(evaluator)
    response = make_text_response("Hi") # Length < 10
    
    decision = rule.evaluate(response, state, policy)
    assert decision is not None
    assert decision.decision == Decision.RETRY
    assert "too short" in decision.feedback.lower()

def test_weak_answer_rule_retries_on_low_confidence(state, policy, evaluator):
    rule = WeakAnswerRule(evaluator)
    response = make_text_response("I don't know the answer to this question.") # Contains low confidence marker
    
    decision = rule.evaluate(response, state, policy)
    assert decision is not None
    assert decision.decision == Decision.RETRY
    assert "low confidence" in decision.feedback.lower()

def test_weak_answer_rule_aborts_on_max_retries(state, policy, evaluator):
    rule = WeakAnswerRule(evaluator)
    response = make_text_response("I don't know.")
    state.retry_count = 2
    
    decision = rule.evaluate(response, state, policy)
    assert decision is not None
    assert decision.decision == Decision.ABORT

def test_tool_call_rule(state, policy):
    rule = ToolCallRule()
    response = make_tool_response()
    
    decision = rule.evaluate(response, state, policy)
    assert decision is not None
    assert decision.decision == Decision.CALL_TOOLS

def test_finish_rule(state, policy):
    rule = FinishRule()
    response = make_text_response("This is a valid, long enough response.")
    
    decision = rule.evaluate(response, state, policy)
    assert decision is not None
    assert decision.decision == Decision.FINISH

def test_reasoning_planner_integration(state):
    planner = ReasoningPlanner()
    
    # 1. Test Retry on empty
    resp_empty = make_text_response("")
    dec = planner.decide(resp_empty, state)
    assert dec.decision == Decision.RETRY
    
    # 2. Test Retry on weak
    state.retry_count = 0
    resp_weak = make_text_response("I don't know.")
    dec = planner.decide(resp_weak, state)
    assert dec.decision == Decision.RETRY
    
    # 3. Test Abort on max retries
    state.retry_count = 2
    dec = planner.decide(resp_weak, state)
    assert dec.decision == Decision.ABORT
    
    # 4. Test Call Tools
    state.retry_count = 0
    resp_tools = make_tool_response()
    dec = planner.decide(resp_tools, state)
    assert dec.decision == Decision.CALL_TOOLS
    
    # 5. Test Finish
    resp_good = make_text_response("This is a perfectly good response.")
    dec = planner.decide(resp_good, state)
    assert dec.decision == Decision.FINISH