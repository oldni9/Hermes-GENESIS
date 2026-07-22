"""
===============================================================================
Tests for Tree of Thought Planner (Sprint 10)
===============================================================================
"""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from hermes.ai.conversation import AIConversation
from hermes.ai.response import AIResponse, ResponseUsage
from hermes.agent.executor.engine import ExecutionEngine
from hermes.agent.executor.planners.tree_of_thought import TreeOfThoughtPlanner, StructuredListParser
from hermes.agent.executor.planners.base import TreeOfThoughtConfig, PlannerState
from hermes.agent.executor.trace import AgentTrace, TraceEventType
from hermes.core.runtime import RuntimeContext
from hermes.core.errors import DeadlineExceeded, BudgetExceeded, ExecutionCancelled


def make_tot_response(text: str, tokens: int = 10) -> AIResponse:
    """Helper for ToT LLM responses."""
    usage = ResponseUsage(prompt_tokens=tokens//2, completion_tokens=tokens//2, total_tokens=tokens)
    return AIResponse(success=True, result=text, provider="test", model="test-model", usage=usage)


@pytest.fixture
def mock_engine() -> MagicMock:
    """Mocks the ExecutionEngine directly to test Planner logic in isolation."""
    engine = MagicMock(spec=ExecutionEngine)
    engine.provider = "test"
    engine.model = "test-model"
    return engine

@pytest.fixture
def planner_state() -> PlannerState:
    return PlannerState(
        conversation=AIConversation(),
        trace=AgentTrace(),
        runtime_context=RuntimeContext()
    )

def test_tot_single_branch_degenerates_to_react(mock_engine: MagicMock, planner_state: PlannerState):
    """If branch_factor=1, it should just pick the single candidate."""
    mock_engine.execute_ephemeral.side_effect = [
        make_tot_response("['Thought 1']"), # Gen
        make_tot_response("[10]"),          # Eval
        make_tot_response("['FINAL ANSWER: Done']"), # Gen 2
        make_tot_response("[10]")           # Eval 2
    ]
    
    config = TreeOfThoughtConfig(branch_factor=1, max_depth=3)
    planner = TreeOfThoughtPlanner()
    
    result = planner.run(mock_engine, planner_state, config)
    
    assert result.stop_reason.value == "completed"
    assert result.response.text() == "Done"
    assert result.iterations == 2

def test_tot_multi_branch_selection(mock_engine: MagicMock, planner_state: PlannerState):
    """Should select the highest scoring branch."""
    mock_engine.execute_ephemeral.side_effect = [
        make_tot_response("['Bad thought', 'Good thought', 'Okay thought']"), # Gen
        make_tot_response("[2, 9, 5]"),                                       # Eval
    ]
    
    config = TreeOfThoughtConfig(branch_factor=3, max_depth=1)
    planner = TreeOfThoughtPlanner()
    
    result = planner.run(mock_engine, planner_state, config)
    
    selected_events = [e for e in planner_state.trace.events if e.event_type == TraceEventType.TOT_BRANCH_SELECTED]
    assert len(selected_events) == 1
    assert selected_events[0].payload["thought"] == "Good thought"
    assert selected_events[0].payload["branch_id"] == "b1_1"

def test_tot_max_depth_stopping(mock_engine: MagicMock, planner_state: PlannerState):
    """Should stop if max_depth is reached without a final answer."""
    mock_engine.execute_ephemeral.side_effect = [
        make_tot_response("['Thought 1']"), # Gen 1
        make_tot_response("[8]"),           # Eval 1
        make_tot_response("['Thought 2']"), # Gen 2
        make_tot_response("[8]")            # Eval 2
    ]
    
    config = TreeOfThoughtConfig(branch_factor=1, max_depth=2)
    planner = TreeOfThoughtPlanner()
    
    result = planner.run(mock_engine, planner_state, config)
    
    assert result.stop_reason.value == "max_iterations"
    assert result.iterations == 2
    assert "max depth" in result.response.message.lower()

def test_tot_trace_events_emitted(mock_engine: MagicMock, planner_state: PlannerState):
    """Verify all required ToT trace events are emitted."""
    mock_engine.execute_ephemeral.side_effect = [
        make_tot_response("['Thought 1']"), # Gen
        make_tot_response("[10]"),          # Eval
        make_tot_response("['FINAL ANSWER: Done']"), # Gen 2
        make_tot_response("[10]")           # Eval 2
    ]
    
    config = TreeOfThoughtConfig(branch_factor=1, max_depth=3)
    planner = TreeOfThoughtPlanner()
    planner.run(mock_engine, planner_state, config)
    
    event_types = [e.event_type for e in planner_state.trace.events]
    
    assert TraceEventType.TOT_BRANCH_GENERATED in event_types
    assert TraceEventType.TOT_BRANCH_EVALUATED in event_types
    assert TraceEventType.TOT_BRANCH_SELECTED in event_types
    assert TraceEventType.TOT_SEARCH_FINISHED in event_types

def test_tot_zero_branch_edge_case(mock_engine: MagicMock, planner_state: PlannerState):
    """If generation returns empty list or unparseable text, should fail gracefully."""
    mock_engine.execute_ephemeral.side_effect = [
        make_tot_response("I cannot generate thoughts"), # Gen
    ]
    
    config = TreeOfThoughtConfig(branch_factor=3, max_depth=3)
    planner = TreeOfThoughtPlanner()
    
    result = planner.run(mock_engine, planner_state, config)
    
    assert result.stop_reason.value == "pipeline_error"
    assert "0 candidates" in result.response.message

def test_tot_numbered_list_parsing(mock_engine: MagicMock, planner_state: PlannerState):
    """Verify the parser can handle numbered lists if JSON/literal_eval fails."""
    mock_engine.execute_ephemeral.side_effect = [
        make_tot_response("1. First thought\n2. Second thought"), # Gen
        make_tot_response("[5, 9]"),                              # Eval
    ]
    
    config = TreeOfThoughtConfig(branch_factor=2, max_depth=1)
    planner = TreeOfThoughtPlanner()
    
    result = planner.run(mock_engine, planner_state, config)
    
    selected_events = [e for e in planner_state.trace.events if e.event_type == TraceEventType.TOT_BRANCH_SELECTED]
    assert selected_events[0].payload["thought"] == "Second thought"

def test_tot_does_not_pollute_conversation(mock_engine: MagicMock, planner_state: PlannerState):
    """Verify ephemeral prompts do not permanently mutate the conversation history."""
    mock_engine.execute_ephemeral.side_effect = [
        make_tot_response("['Thought 1']"), # Gen
        make_tot_response("[10]"),          # Eval
        make_tot_response("['FINAL ANSWER: Done']"), # Gen 2
        make_tot_response("[10]")           # Eval 2
    ]
    
    config = TreeOfThoughtConfig(branch_factor=1, max_depth=3)
    planner = TreeOfThoughtPlanner()
    planner.run(mock_engine, planner_state, config)
    
    # Conversation should only contain the final assistant message
    # It should NOT contain the generator or evaluator prompts.
    messages = planner_state.conversation.messages()
    assert len(messages) == 1
    assert messages[0].role.value == "assistant"
    assert messages[0].content == "Done"

def test_structured_list_parser():
    # JSON
    assert StructuredListParser.parse('["a", "b"]') == ["a", "b"]
    # literal_eval
    assert StructuredListParser.parse("['a', 'b']") == ["a", "b"]
    # Numbered list
    assert StructuredListParser.parse("1. First\n2. Second") == ["First", "Second"]
    # Markdown bullets
    assert StructuredListParser.parse("- First\n- Second") == ["First", "Second"]
    assert StructuredListParser.parse("* First\n* Second") == ["First", "Second"]
    assert StructuredListParser.parse("• First\n• Second") == ["First", "Second"]
    # Tuples should not parse to lists
    assert StructuredListParser.parse("('a', 'b')") == []