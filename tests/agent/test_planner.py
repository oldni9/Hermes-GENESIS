import pytest
from unittest.mock import MagicMock

from hermes.ai.conversation import AIConversation
from hermes.ai.response import AIResponse, ResponseChoice, ResponseMessage
from hermes.agent.executor import AgentExecutor, AgentTrace, PlannerConfig
from hermes.agent.executor.planners.reflection import ReflectionPlanner
from hermes.agent.executor.planners.react import ReActPlanner
from hermes.agent.executor.protocols import PipelineProtocol
from hermes.ai.tool import ToolManager, ToolRegistry


@pytest.fixture
def mock_pipeline():
    return MagicMock(spec=PipelineProtocol)

@pytest.fixture
def tool_manager():
    # FIX: Use ToolRegistry instead of Registry
    return ToolManager(ToolRegistry())

@pytest.fixture
def conversation():
    return AIConversation(title="Test Reflection")

def make_text_response(text: str) -> AIResponse:
    choice = ResponseChoice(
        index=0,
        message=ResponseMessage(role="assistant", content=text),
        finish_reason="stop"
    )
    return AIResponse(success=True, provider="test", model="test-model", choices=[choice], result=text)

def test_reflection_planner_approves_immediately(mock_pipeline, tool_manager):
    # Engine returns "42". Critic approves.
    mock_pipeline.execute.side_effect = [
        make_text_response("42"),          # Engine turn 1
        make_text_response("APPROVED")     # Critic turn 1
    ]
    
    planner = ReflectionPlanner(mock_pipeline, "test", "test-model")
    agent = AgentExecutor(
        pipeline=mock_pipeline,
        tool_manager=tool_manager,
        provider="test",
        model="test-model",
        planner=planner,
        config=PlannerConfig(max_iterations=5)
    )
    
    result = agent.run("What is 40+4?", AIConversation())
    
    assert result.response.success
    assert result.response.text() == "42"
    assert result.iterations == 1
    assert result.stop_reason == "completed"

def test_reflection_planner_rejects_and_retries(mock_pipeline, tool_manager):
    # Engine returns "42". Critic rejects. Engine returns "44". Critic approves.
    mock_pipeline.execute.side_effect = [
        make_text_response("42"),          # Engine turn 1
        make_text_response("REJECT: 42 is wrong."), # Critic turn 1
        make_text_response("44"),          # Engine turn 2
        make_text_response("APPROVED")     # Critic turn 2
    ]
    
    planner = ReflectionPlanner(mock_pipeline, "test", "test-model")
    agent = AgentExecutor(
        pipeline=mock_pipeline,
        tool_manager=tool_manager,
        provider="test",
        model="test-model",
        planner=planner,
        config=PlannerConfig(max_iterations=5, max_reflections=2)
    )
    
    result = agent.run("What is 40+4?", AIConversation())
    
    assert result.response.success
    assert result.response.text() == "44"
    assert result.iterations == 2
    assert result.stop_reason == "completed"

def test_reflection_planner_stops_at_max_reflections(mock_pipeline, tool_manager):
    # Critic always says REJECT
    mock_pipeline.execute.side_effect = [
        make_text_response("42"),
        make_text_response("REJECT: Still wrong."),
        make_text_response("43"),
        make_text_response("REJECT: Still wrong.")
    ]
    
    planner = ReflectionPlanner(mock_pipeline, "test", "test-model")
    agent = AgentExecutor(
        pipeline=mock_pipeline,
        tool_manager=tool_manager,
        provider="test",
        model="test-model",
        planner=planner,
        config=PlannerConfig(max_iterations=5, max_reflections=2)
    )
    
    result = agent.run("What is 40+4?", AIConversation())
    
    assert not result.response.success
    assert result.stop_reason == "max_reflections"
    assert result.iterations == 2