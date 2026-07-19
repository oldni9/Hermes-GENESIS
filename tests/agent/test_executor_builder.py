"""
===============================================================================
Tests for Agent Request Builder
===============================================================================
"""

import pytest
from hermes.agent.executor.builder import RequestBuilder
from hermes.ai.conversation import AIConversation
from hermes.ai.response import ToolCall, FunctionCall


@pytest.fixture
def conversation():
    return AIConversation(title="Test Builder Session")

def test_builder_basic_user_assistant(conversation):
    """Ensure basic messages are mapped correctly."""
    conversation.add_user("Hello")
    conversation.add_assistant("Hi there")
    
    messages = RequestBuilder.build(conversation)
    
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Hello"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["content"] == "Hi there"

def test_builder_maps_tool_calls(conversation):
    """Ensure tool_calls and tool_call_ids are mapped perfectly."""
    tc = ToolCall(id="tc1", type="function", function=FunctionCall(name="test", arguments={"x": 1}))
    conversation.add_user("Use tool")
    conversation.add_message(role="assistant", content="", tool_calls=[tc])
    conversation.add_message(role="tool", content="result", tool_call_id="tc1", name="test")
    
    messages = RequestBuilder.build(conversation)
    
    assert len(messages) == 3
    assert messages[1]["role"] == "assistant"
    assert messages[1]["tool_calls"] is not None
    assert messages[1]["tool_calls"][0]["id"] == "tc1"
    assert messages[2]["role"] == "tool"
    assert messages[2]["tool_call_id"] == "tc1"

def test_builder_appends_transient_messages(conversation):
    """Verify that transient messages are appended at the end without mutating conversation."""
    conversation.add_user("Hi")
    
    transient = [
        {"role": "assistant", "content": "Previous bad response"},
        {"role": "system", "content": "Please try again."}
    ]
    
    messages = RequestBuilder.build(conversation, transient_messages=transient)
    
    assert len(messages) == 3
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["content"] == "Previous bad response"
    assert messages[2]["role"] == "system"
    assert messages[2]["content"] == "Please try again."
    
    # Ensure original conversation is untouched
    assert len(conversation) == 1