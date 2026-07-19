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
from hermes.agent.planner.policy import PlannerPolicy  # FIX: Added missing import
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
    """Test that the agent returns immediately if no tools are called and response is good."""
    mock_pipeline.execute.return_value = make_text_response("Hello! How can I help you today?")
    
    agent = AgentExecutor(
        pipeline=mock_pipeline,
        tool_manager=mock_tool_manager,
        provider="test",
        model="test-model",
        planner=ReasoningPlanner() # Use ReasoningPlanner
    )
    
    response = agent.run("Hi", conversation)
    
    assert response.success
    assert response.text() == "Hello! How can I help you today?"
    assert len(conversation) == 2  # User + Assistant
    mock_pipeline.execute.assert_called_once()
    mock_tool_manager.execute_batch.assert_not_called()

def test_agent_retry_does_not_mutate_conversation(mock_pipeline, mock_tool_manager, conversation):
    """Test that RETRY decisions inject transient messages without polluting AIConversation."""
    mock_pipeline.execute.side_effect = [
        make_text_response(""),  # 1. Empty response -> triggers RETRY
        make_text_response("This is a good response.") # 2. Good response -> triggers FINISH
    ]
    
    agent = AgentExecutor(
        pipeline=mock_pipeline,
        tool_manager=mock_tool_manager,
        provider="test",
        model="test-model",
        planner=ReasoningPlanner(policy=PlannerPolicy(minimum_response_length=5)) # Explicit policy
    )
    
    response = agent.run("Hi", conversation)
    
    assert response.success
    assert response.text() == "This is a good response."
    
    # Conversation should ONLY contain User and final Assistant message.
    # The empty response and system feedback should NOT be in AIConversation.
    assert len(conversation) == 2
    msgs = conversation.messages()
    assert msgs[0].role.value == "user"
    assert msgs[1].role.value == "assistant"
    assert msgs[1].content == "This is a good response."
    
    # Verify the pipeline was called twice (1 retry)
    assert mock_pipeline.execute.call_count == 2
    
    # Verify the 2nd call to pipeline contained transient messages
    second_call_request = mock_pipeline.execute.call_args_list[1].kwargs["request"]
    sent_messages = second_call_request.options["messages"]
    
    # 1 User + 1 Transient Assistant + 1 Transient System = 3 messages
    assert len(sent_messages) == 3
    assert sent_messages[1]["role"] == "assistant"
    assert sent_messages[1]["content"] == "" # The empty response
    assert sent_messages[2]["role"] == "system"
    assert "empty" in sent_messages[2]["content"].lower() # FIX: More flexible assertion

def test_agent_abort_returns_error_response(mock_pipeline, mock_tool_manager, conversation):
    """Test that ABORT decision returns a failed AIResponse."""
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
    
    # Verify response is an error, even though LLM returned text
    assert not response.success
    assert "Execution aborted: Custom abort reason" in response.message

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
        planner=ReasoningPlanner()
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
    assert messages[2].content == "12"
    assert messages[3].role.value == "assistant"
    assert messages[3].content == "The result is 12."
    
    second_call_request = mock_pipeline.execute.call_args_list[1].kwargs["request"]
    sent_messages = second_call_request.options["messages"]
    
    assert len(sent_messages) == 3
    assert sent_messages[0]["role"] == "user"
    assert sent_messages[1]["role"] == "assistant"
    assert sent_messages[1]["tool_calls"] is not None
    assert sent_messages[2]["role"] == "tool"
    assert sent_messages[2]["tool_call_id"] == "call_1"