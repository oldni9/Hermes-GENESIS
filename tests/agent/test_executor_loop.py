"""
===============================================================================
Tests for Agent Executor Loop
===============================================================================
"""

import pytest
from unittest.mock import MagicMock

from hermes.agent.executor.loop import AgentExecutor
from hermes.agent.executor.context_factory import AgentContextFactory
from hermes.agent.planner.reasoning_planner import ReasoningPlanner
from hermes.agent.planner.policy import PlannerPolicy
from hermes.agent.planner.decision import Decision, PlannerDecision
from hermes.agent.planner.hasher import ToolCallHasher
from hermes.ai.conversation import AIConversation
from hermes.ai.pipeline import AIPipeline
from hermes.ai.request import AIRequest
from hermes.ai.response import AIResponse, ToolCall, FunctionCall, ResponseChoice, ResponseMessage
from hermes.ai.tool import ToolManager, ToolRegistry, ToolResult, ToolStatus, ToolContext
from hermes.workspace.context import ExecutionContext


@pytest.fixture
def mock_pipeline():
    return MagicMock(spec=AIPipeline)

@pytest.fixture
def mock_tool_manager():
    tm = ToolManager(ToolRegistry())
    tm.register_function(name="search", func=lambda query: "result", description="Search")
    return tm

@pytest.fixture
def conversation():
    return AIConversation(title="Test Loop Session")

def make_text_response(text: str) -> AIResponse:
    choice = ResponseChoice(
        index=0,
        message=ResponseMessage(role="assistant", content=text),
        finish_reason="stop"
    )
    return AIResponse(success=True, provider="test", model="test-model", choices=[choice], result=text)

def make_tool_response(call_id: str, func_name: str, args: dict = None) -> AIResponse:
    tc = ToolCall(id=call_id, type="function", function=FunctionCall(name=func_name, arguments=args or {}))
    choice = ResponseChoice(
        index=0,
        message=ResponseMessage(role="assistant", content=""),
        finish_reason="tool_calls"
    )
    return AIResponse(success=True, provider="test", model="test-model", choices=[choice], tool_calls=[tc])

def test_agent_no_tools(mock_pipeline, mock_tool_manager, conversation):
    mock_pipeline.execute.return_value = make_text_response("Hello! How can I help you today?")
    agent = AgentExecutor(
        pipeline=mock_pipeline,
        tool_manager=mock_tool_manager,
        provider="test",
        model="test-model",
        planner=ReasoningPlanner(registry=mock_tool_manager.registry)
    )
    response = agent.run("Hi", conversation)
    assert response.success
    assert response.text() == "Hello! How can I help you today?"
    assert len(conversation) == 2
    mock_pipeline.execute.assert_called_once()

def test_agent_injects_execution_context(mock_pipeline, mock_tool_manager, conversation):
    """Test that ExecutionContext IDs are propagated to AIRequest metadata."""
    mock_pipeline.execute.return_value = make_text_response("Done.")
    
    agent = AgentExecutor(
        pipeline=mock_pipeline,
        tool_manager=mock_tool_manager,
        provider="test",
        model="test-model",
        planner=ReasoningPlanner(registry=mock_tool_manager.registry)
    )
    
    ctx = ExecutionContext.create(workspace_id="ws_test", metadata={"trace": True})
    agent.run("Hi", conversation, execution_context=ctx)
    
    _, kwargs = mock_pipeline.execute.call_args
    request: AIRequest = kwargs["request"]
    assert request.metadata["execution_id"] == ctx.execution_id

def test_agent_retry_does_not_mutate_conversation(mock_pipeline, mock_tool_manager, conversation):
    mock_pipeline.execute.side_effect = [
        make_text_response(""),
        make_text_response("This is a good response.")
    ]
    agent = AgentExecutor(
        pipeline=mock_pipeline,
        tool_manager=mock_tool_manager,
        provider="test",
        model="test-model",
        planner=ReasoningPlanner(policy=PlannerPolicy(minimum_response_length=5), registry=mock_tool_manager.registry)
    )
    response = agent.run("Hi", conversation)
    assert response.success
    assert response.text() == "This is a good response."
    assert len(conversation) == 2
    second_call_request = mock_pipeline.execute.call_args_list[1].kwargs["request"]
    sent_messages = second_call_request.options["messages"]
    assert len(sent_messages) == 3
    assert sent_messages[2]["role"] == "system"

def test_agent_abort_returns_error_response(mock_pipeline, mock_tool_manager, conversation):
    mock_planner = MagicMock(spec=ReasoningPlanner)
    mock_planner.decide.return_value = PlannerDecision(
        decision=Decision.ABORT,
        reason="Custom abort reason"
    )
    mock_pipeline.execute.return_value = make_text_response("Some text")
    agent = AgentExecutor(
        pipeline=mock_pipeline,
        tool_manager=mock_tool_manager,
        provider="test",
        model="test-model",
        planner=mock_planner
    )
    response = agent.run("Hi", conversation)
    assert not response.success
    assert "Execution aborted: Custom abort reason" in response.message

def test_agent_records_failure_history(mock_pipeline, mock_tool_manager, conversation):
    mock_pipeline.execute.side_effect = [
        make_tool_response("c1", "search", {"q": "test"}),
        make_tool_response("c2", "search", {"q": "test"}),
        make_text_response("I couldn't find it.")
    ]
    mock_tool_manager.execute_batch = MagicMock(return_value=[
        ToolResult(call_id="c1", status=ToolStatus.FAILED, error="API Down"),
        ToolResult(call_id="c2", status=ToolStatus.FAILED, error="API Down")
    ])
    agent = AgentExecutor(
        pipeline=mock_pipeline,
        tool_manager=mock_tool_manager,
        provider="test",
        model="test-model",
        planner=ReasoningPlanner(registry=mock_tool_manager.registry)
    )
    response = agent.run("Search for test", conversation)
    assert not response.success
    assert "Execution aborted: Repeated failure detected" in response.message
    assert mock_pipeline.execute.call_count == 2

def test_agent_full_loop_openai_ordering(mock_pipeline, mock_tool_manager, conversation):
    mock_pipeline.execute.side_effect = [
        make_tool_response("call_1", "search", {"q": "hello"}),
        make_text_response("The result is 12.")
    ]
    mock_tool_manager.execute_batch = MagicMock(return_value=[
        ToolResult(call_id="call_1", status=ToolStatus.SUCCESS, output="Found it")
    ])
    agent = AgentExecutor(
        pipeline=mock_pipeline,
        tool_manager=mock_tool_manager,
        provider="test",
        model="test-model",
        planner=ReasoningPlanner(registry=mock_tool_manager.registry)
    )
    response = agent.run("What is 5 + 7?", conversation)
    assert response.success
    assert response.text() == "The result is 12."
    messages = conversation.messages()
    assert len(messages) == 4
    assert messages[0].role.value == "user"
    assert messages[1].role.value == "assistant"
    assert messages[1].tool_calls is not None
    assert messages[2].role.value == "tool"
    assert messages[2].content == "Found it"
    assert messages[3].role.value == "assistant"
    assert messages[3].content == "The result is 12."