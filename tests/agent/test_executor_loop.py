"""
===============================================================================
Tests for Agent Executor Loop
===============================================================================
"""

import pytest
from unittest.mock import MagicMock

from hermes.agent.executor.loop import AgentExecutor
from hermes.agent.executor.context_factory import AgentContextFactory
from hermes.agent.planner.planner import DefaultPlanner
from hermes.agent.planner.decision import Decision, PlannerDecision
from hermes.ai.conversation import AIConversation
from hermes.ai.pipeline import AIPipeline
from hermes.ai.request import AIRequest
from hermes.ai.response import AIResponse, ToolCall, FunctionCall, ResponseChoice, ResponseMessage
from hermes.ai.tool import ToolManager, ToolResult, ToolStatus, ToolContext


@pytest.fixture
def mock_pipeline():
    return MagicMock(spec=AIPipeline)

@pytest.fixture
def mock_tool_manager():
    return MagicMock(spec=ToolManager)

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
    """Test that the agent returns immediately if no tools are called."""
    mock_pipeline.execute.return_value = make_text_response("Hello! How can I help you?")
    
    agent = AgentExecutor(
        pipeline=mock_pipeline,
        tool_manager=mock_tool_manager,
        provider="test",
        model="test-model",
        max_iterations=5
    )
    
    response = agent.run("Hi", conversation)
    
    assert response.success
    assert response.text() == "Hello! How can I help you?"
    assert len(conversation) == 2  # User + Assistant
    mock_pipeline.execute.assert_called_once()
    mock_tool_manager.execute_batch.assert_not_called()

def test_agent_full_loop_openai_ordering(mock_pipeline, mock_tool_manager, conversation):
    """Test the full agent loop with a single tool call and verify OpenAI message ordering."""
    mock_pipeline.execute.side_effect = [
        make_tool_response("call_1", "add", {"a": 5, "b": 7}),
        make_text_response("The result is 12.")
    ]
    
    mock_tool_manager.execute_batch.return_value = [
        ToolResult(call_id="call_1", status=ToolStatus.SUCCESS, output=12)
    ]
    
    agent = AgentExecutor(
        pipeline=mock_pipeline,
        tool_manager=mock_tool_manager,
        provider="test",
        model="test-model",
        max_iterations=5
    )
    
    response = agent.run("What is 5 + 7?", conversation)
    
    assert response.success
    assert response.text() == "The result is 12."
    
    # Verify conversation history
    messages = conversation.messages()
    assert len(messages) == 4
    assert messages[0].role.value == "user"
    assert messages[1].role.value == "assistant"
    assert messages[1].tool_calls is not None
    assert messages[2].role.value == "tool"
    assert messages[2].content == "12"
    assert messages[2].metadata.get("tool_call_id") == "call_1"
    assert messages[3].role.value == "assistant"
    assert messages[3].content == "The result is 12."
    
    # Verify the exact request payload sent to the pipeline on the 2nd iteration
    second_call_request = mock_pipeline.execute.call_args_list[1].kwargs["request"]
    sent_messages = second_call_request.options["messages"]
    
    assert len(sent_messages) == 3
    assert sent_messages[0]["role"] == "user"
    assert sent_messages[1]["role"] == "assistant"
    assert sent_messages[1]["tool_calls"] is not None
    assert sent_messages[2]["role"] == "tool"
    assert sent_messages[2]["tool_call_id"] == "call_1"

def test_agent_max_iterations(mock_pipeline, mock_tool_manager, conversation):
    """Test that the agent stops after max iterations."""
    mock_pipeline.execute.return_value = make_tool_response("call_1", "add", {"a": 1, "b": 1})
    mock_tool_manager.execute_batch.return_value = [
        ToolResult(call_id="call_1", status=ToolStatus.SUCCESS, output=2)
    ]
    
    agent = AgentExecutor(
        pipeline=mock_pipeline,
        tool_manager=mock_tool_manager,
        provider="test",
        model="test-model",
        max_iterations=3
    )
    
    response = agent.run("Keep adding", conversation)
    
    assert not response.success
    assert "maximum iterations" in response.message.lower()
    assert mock_pipeline.execute.call_count == 3

def test_agent_tool_execution_error_propagation(mock_pipeline, mock_tool_manager, conversation):
    """Test that tool execution errors are fed back to the LLM."""
    mock_pipeline.execute.side_effect = [
        make_tool_response("call_1", "fail_tool", {}),
        make_text_response("Sorry, that tool failed.")
    ]
    
    mock_tool_manager.execute_batch.return_value = [
        ToolResult(call_id="call_1", status=ToolStatus.FAILED, error="Database connection lost")
    ]
    
    agent = AgentExecutor(
        pipeline=mock_pipeline,
        tool_manager=mock_tool_manager,
        provider="test",
        model="test-model",
        max_iterations=5
    )
    
    response = agent.run("Use failing tool", conversation)
    
    assert response.success
    assert response.text() == "Sorry, that tool failed."
    
    messages = conversation.messages()
    assert len(messages) == 4
    assert messages[2].role.value == "tool"
    assert "Error executing tool 'fail_tool': Database connection lost" in messages[2].content

def test_agent_multiple_tool_calls(mock_pipeline, mock_tool_manager, conversation):
    """Test multiple tool calls in a single assistant response."""
    multi_call_response = AIResponse(
        success=True,
        provider="test",
        model="test-model",
        choices=[ResponseChoice(index=0, message=ResponseMessage(role="assistant", content=""), finish_reason="tool_calls")],
        tool_calls=[
            ToolCall(id="c1", type="function", function=FunctionCall(name="add", arguments={"a":1, "b":1})),
            ToolCall(id="c2", type="function", function=FunctionCall(name="add", arguments={"a":2, "b":2}))
        ]
    )
    mock_pipeline.execute.side_effect = [multi_call_response, make_text_response("Done")]
    
    mock_tool_manager.execute_batch.return_value = [
        ToolResult(call_id="c1", status=ToolStatus.SUCCESS, output=2),
        ToolResult(call_id="c2", status=ToolStatus.SUCCESS, output=4)
    ]
    
    agent = AgentExecutor(
        pipeline=mock_pipeline,
        tool_manager=mock_tool_manager,
        provider="test",
        model="test-model",
        max_iterations=5
    )
    
    response = agent.run("Add 1+1 and 2+2", conversation)
    
    assert response.success
    
    messages = conversation.messages()
    # user, assistant(tool_calls), tool(c1), tool(c2), assistant(final)
    assert len(messages) == 5
    
    assert messages[2].role.value == "tool"
    assert messages[2].content == "2"
    assert messages[2].metadata.get("tool_call_id") == "c1"
    
    assert messages[3].role.value == "tool"
    assert messages[3].content == "4"
    assert messages[3].metadata.get("tool_call_id") == "c2"

def test_agent_cache_disabled_by_default(mock_pipeline, mock_tool_manager, conversation):
    """Test that use_cache=False is passed to the pipeline by default."""
    mock_pipeline.execute.return_value = make_text_response("Hi")
    
    agent = AgentExecutor(
        pipeline=mock_pipeline,
        tool_manager=mock_tool_manager,
        provider="test",
        model="test-model"
    )
    
    agent.run("Hello", conversation)
    
    _, kwargs = mock_pipeline.execute.call_args
    assert kwargs.get("use_cache") is False

def test_agent_cache_enabled(mock_pipeline, mock_tool_manager, conversation):
    """Test that use_cache=True is passed when configured."""
    mock_pipeline.execute.return_value = make_text_response("Hi")
    
    agent = AgentExecutor(
        pipeline=mock_pipeline,
        tool_manager=mock_tool_manager,
        provider="test",
        model="test-model",
        use_cache=True
    )
    
    agent.run("Hello", conversation)
    
    _, kwargs = mock_pipeline.execute.call_args
    assert kwargs.get("use_cache") is True

def test_agent_passes_context_to_tools(mock_pipeline, mock_tool_manager, conversation):
    """Test that AgentExecutor builds a context and passes it to the tool runner."""
    mock_pipeline.execute.side_effect = [
        make_tool_response("call_1", "search", {"q": "test"}),
        make_text_response("Done")
    ]
    
    mock_tool_manager.execute_batch.return_value = [
        ToolResult(call_id="call_1", status=ToolStatus.SUCCESS, output="Result")
    ]
    
    agent = AgentExecutor(
        pipeline=mock_pipeline,
        tool_manager=mock_tool_manager,
        provider="test",
        model="test-model"
    )
    
    agent.run("Search for test", conversation)
    
    # Verify execute_batch was called with a context
    _, kwargs = mock_tool_manager.execute_batch.call_args
    assert "context" in kwargs
    assert kwargs["context"] is not None
    assert isinstance(kwargs["context"], ToolContext)
    assert kwargs["context"].conversation is conversation

def test_agent_uses_custom_context_factory(mock_pipeline, mock_tool_manager, conversation):
    """Test that a custom context factory can be injected."""
    mock_factory = MagicMock(spec=AgentContextFactory)
    custom_context = ToolContext(session="custom-session")
    mock_factory.build.return_value = custom_context
    
    mock_pipeline.execute.side_effect = [
        make_tool_response("call_1", "search", {"q": "test"}),
        make_text_response("Done")
    ]
    
    mock_tool_manager.execute_batch.return_value = [
        ToolResult(call_id="call_1", status=ToolStatus.SUCCESS, output="Result")
    ]
    
    agent = AgentExecutor(
        pipeline=mock_pipeline,
        tool_manager=mock_tool_manager,
        provider="test",
        model="test-model",
        context_factory=mock_factory
    )
    
    agent.run("Search for test", conversation)
    
    # Verify the custom factory was used
    mock_factory.build.assert_called_once_with(conversation)
    
    # Verify the custom context was passed down
    _, kwargs = mock_tool_manager.execute_batch.call_args
    assert kwargs.get("context") is custom_context

def test_agent_uses_custom_planner(mock_pipeline, mock_tool_manager, conversation):
    """Test that a custom planner can be injected and overrides default behavior."""
    mock_planner = MagicMock(spec=DefaultPlanner)
    
    # Force the planner to always decide to ABORT, even if the response is successful
    mock_planner.decide.return_value = PlannerDecision(
        decision=Decision.ABORT,
        reason="Custom planner abort"
    )
    
    mock_pipeline.execute.return_value = make_text_response("Hello")
    
    agent = AgentExecutor(
        pipeline=mock_pipeline,
        tool_manager=mock_tool_manager,
        provider="test",
        model="test-model",
        planner=mock_planner
    )
    
    response = agent.run("Hi", conversation)
    
    # Verify the custom planner was called
    mock_planner.decide.assert_called_once()
    
    # Verify the executor honored the ABORT decision and returned immediately
    # without appending the assistant message to the conversation
    assert len(conversation) == 1 # Only the user message
    assert response.success # The response itself was successful