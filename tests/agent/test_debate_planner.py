"""
===============================================================================
Tests for Debate Planner (Sprint 11 & 12)
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
from hermes.runtime.parallel import ParallelResult
from hermes.core.runtime import RuntimeContext


def make_debate_response(text: str, tokens: int = 10) -> AIResponse:
    usage = ResponseUsage(prompt_tokens=tokens//2, completion_tokens=tokens//2, total_tokens=tokens)
    return AIResponse(success=True, result=text, provider="test", model="test-model", usage=usage)


def run_jobs_sequentially(trace, iteration, config, jobs):
    """Helper to simulate engine.execute_parallel by running jobs sequentially and emitting engine trace events."""
    trace.add_event(iteration, TraceEventType.PARALLEL_STARTED, {"jobs": len(jobs), "workers": 1})
    results = []
    for job in jobs:
        try:
            val = job.fn()
            results.append(ParallelResult(id=job.id, success=True, value=val))
        except Exception as e:
            results.append(ParallelResult(id=job.id, success=False, exception=e))
    trace.add_event(iteration, TraceEventType.PARALLEL_COMPLETED, {"jobs": len(results)})
    return results


@pytest.fixture
def mock_engine() -> MagicMock:
    engine = MagicMock(spec=ExecutionEngine)
    engine.provider = "test"
    engine.model = "test-model"
    # Make execute_parallel actually run the jobs so trace events fire
    engine.execute_parallel.side_effect = run_jobs_sequentially
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
    """Should execute ephemeral calls for each debater (via parallel) and one for the judge."""
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
    
    assert mock_engine.execute_parallel.call_count == 1
    assert mock_engine.execute_ephemeral.call_count == 4 # 3 debaters + 1 judge
    assert result.stop_reason.value == "completed"
    assert result.response.text() == "All languages have tradeoffs."

def test_debate_trace_events_emitted(mock_engine: MagicMock, planner_state: PlannerState):
    """Verify all required Debate and Parallel trace events are emitted."""
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
    
    # Sprint 12 Parallel Events
    assert TraceEventType.PARALLEL_STARTED in event_types
    assert TraceEventType.PARALLEL_JOB_STARTED in event_types
    assert TraceEventType.PARALLEL_JOB_FINISHED in event_types
    assert TraceEventType.PARALLEL_COMPLETED in event_types

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

def test_debate_tolerates_partial_failures(mock_engine: MagicMock, planner_state: PlannerState):
    """Should proceed to Judge even if some debaters fail."""
    # Analyst succeeds, Skeptic fails, Creative succeeds, Judge succeeds
    mock_engine.execute_ephemeral.side_effect = [
        make_debate_response("Python is best."),
        AIResponse(success=False, message="API Error"),
        make_debate_response("JS is everywhere."),
        make_debate_response("All languages have tradeoffs.")
    ]
    
    config = DebateConfig(debaters=3, personas=[
        DebaterPersona(name="Analyst", system_prompt=""),
        DebaterPersona(name="Skeptic", system_prompt=""),
        DebaterPersona(name="Creative", system_prompt="")
    ])
    planner = DebatePlanner()
    result = planner.run(mock_engine, planner_state, config)
    
    assert result.stop_reason.value == "completed"
    # Verify judge prompt only contained 2 responses
    judge_call_args = mock_engine.execute_ephemeral.call_args[0][3]
    assert "Analyst" in judge_call_args
    assert "Creative" in judge_call_args
    assert "Skeptic" not in judge_call_args

def test_debate_fails_if_all_debaters_fail(mock_engine: MagicMock, planner_state: PlannerState):
    """Should fail if 0 debaters succeed."""
    mock_engine.execute_ephemeral.side_effect = [
        AIResponse(success=False, message="API Error"),
        AIResponse(success=False, message="API Error"),
        AIResponse(success=False, message="API Error"),
    ]
    
    config = DebateConfig(debaters=3, personas=[
        DebaterPersona(name="Analyst", system_prompt=""),
        DebaterPersona(name="Skeptic", system_prompt=""),
        DebaterPersona(name="Creative", system_prompt="")
    ])
    planner = DebatePlanner()
    result = planner.run(mock_engine, planner_state, config)
    
    assert result.stop_reason.value == "pipeline_error"
    assert "All debaters failed" in result.response.message
    # Judge should not run (only 3 calls for debaters)
    assert mock_engine.execute_ephemeral.call_count == 3