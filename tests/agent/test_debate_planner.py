"""
===============================================================================
Tests for Debate Planner (Sprint 11)
===============================================================================
"""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from hermes.ai.conversation import AIConversation
from hermes.ai.response import AIResponse, ResponseUsage
from hermes.agent.executor.engine import ExecutionEngine
from hermes.agent.executor.planners.debate import DebatePlanner
from hermes.agent.executor.planners.base import DebateConfig, DebaterPersona, PlannerState
from hermes.agent.executor.trace import AgentTrace, TraceEventType
from hermes.core.runtime import RuntimeContext


def make_debate_response(text: str, tokens: int = 10) -> AIResponse:
    usage = ResponseUsage(prompt_tokens=tokens//2, completion_tokens=tokens//2, total_tokens=tokens)
    return AIResponse(success=True, result=text, provider="test", model="test-model", usage=usage)


@pytest.fixture
def mock_engine() -> MagicMock:
    engine = MagicMock(spec=ExecutionEngine)
    engine.provider = "test"
    engine.model = "test-model"
    return engine

@pytest.fixture
def planner_state() -> PlannerState:
    state = PlannerState(
        conversation=AIConversation(),
        trace=AgentTrace(),
        runtime_context=RuntimeContext(),
        objective="What is the best programming language?"
    )
    return state

def test_debate_runs_all_personas_and_judge(mock_engine: MagicMock, planner_state: PlannerState):
    """Should execute ephemeral calls for each debater and one for the judge."""
    mock_engine.execute_ephemeral.side_effect = [
        make_debate_response("Python is best."),  # Analyst
        make_debate_response("Rust is safer."),   # Skeptic
        make_debate_response("JS is everywhere."),# Creative
        make_debate_response("All languages have tradeoffs.") # Judge
    ]
    
    config = DebateConfig(debaters=3, personas=[
        DebaterPersona(name="Analyst", system_prompt=""),
        DebaterPersona(name="Skeptic", system_prompt=""),
        DebaterPersona(name="Creative", system_prompt="")
    ])
    planner = DebatePlanner()
    
    result = planner.run(mock_engine, planner_state, config)
    
    assert mock_engine.execute_ephemeral.call_count == 4
    assert result.stop_reason.value == "completed"
    assert result.response.text() == "All languages have tradeoffs."

def test_debate_trace_events_emitted(mock_engine: MagicMock, planner_state: PlannerState):
    """Verify all required Debate trace events are emitted."""
    mock_engine.execute_ephemeral.side_effect = [
        make_debate_response("A"), make_debate_response("B"), 
        make_debate_response("C"), make_debate_response("Final")
    ]
    
    config = DebateConfig(debaters=3, personas=[
        DebaterPersona(name="A", system_prompt=""), DebaterPersona(name="B", system_prompt=""), DebaterPersona(name="C", system_prompt="")
    ])
    planner = DebatePlanner()
    planner.run(mock_engine, planner_state, config)
    
    event_types = [e.event_type for e in planner_state.trace.events]
    
    assert TraceEventType.DEBATE_STARTED in event_types
    assert TraceEventType.DEBATER_STARTED in event_types
    assert TraceEventType.DEBATER_RESPONSE in event_types
    assert TraceEventType.DEBATER_FINISHED in event_types
    assert TraceEventType.JUDGE_STARTED in event_types
    assert TraceEventType.JUDGE_FINISHED in event_types
    assert TraceEventType.DEBATE_COMPLETED in event_types

def test_debate_does_not_pollute_conversation(mock_engine: MagicMock, planner_state: PlannerState):
    """Verify ephemeral prompts do not permanently mutate the conversation history."""
    mock_engine.execute_ephemeral.side_effect = [
        make_debate_response("A"), make_debate_response("B"), 
        make_debate_response("C"), make_debate_response("Final")
    ]
    
    config = DebateConfig(debaters=3, personas=[
        DebaterPersona(name="A", system_prompt=""), DebaterPersona(name="B", system_prompt=""), DebaterPersona(name="C", system_prompt="")
    ])
    planner = DebatePlanner()
    planner.run(mock_engine, planner_state, config)
    
    # Conversation should only contain the final Judge answer
    messages = planner_state.conversation.messages()
    assert len(messages) == 1
    assert messages[0].role.value == "assistant"
    assert messages[0].content == "Final"

def test_debate_config_extends_personas():
    """Should auto-extend personas if debaters > len(personas)."""
    config = DebateConfig(debaters=5, personas=[
        DebaterPersona(name="A", system_prompt="")
    ])
    
    assert len(config.personas) == 5
    assert config.personas[1].name == "Debater 2"