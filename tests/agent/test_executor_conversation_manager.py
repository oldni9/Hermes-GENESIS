"""
===============================================================================
Tests for Conversation Manager
===============================================================================
"""

import pytest
from hermes.agent.executor.conversation_manager import ConversationManager
from hermes.ai.conversation import AIConversation
from hermes.ai.response import AIResponse, ToolCall, FunctionCall, ResponseChoice, ResponseMessage
from hermes.ai.tool import ToolResult, ToolStatus


@pytest.fixture
def conversation():
    return AIConversation(title="Test Conv Manager")


@pytest.fixture
def conv_manager(conversation):
    return ConversationManager(conversation)


def make_tool_response(call_id: str, func_name: str) -> AIResponse:
    tc = ToolCall(id=call_id, type="function", function=FunctionCall(name=func_name, arguments={}))
    choice = ResponseChoice(index=0, message=ResponseMessage(role="assistant", content=""), finish_reason="tool_calls")
    return AIResponse(success=True, provider="test", model="test-model", choices=[choice], tool_calls=[tc])


def test_append_system_only_if_empty(conv_manager, conversation):
    conv_manager.append_system("System Init")
    assert len(conversation) == 1
    
    # Should not append a second system message
    conv_manager.append_system("System Update")
    assert len(conversation) == 1
    assert conversation.messages()[0].content == "System Init"


def test_append_user_and_assistant(conv_manager, conversation):
    conv_manager.append_user("Hello")
    conv_manager.append_assistant("Hi")
    
    msgs = conversation.messages()
    assert len(msgs) == 2
    assert msgs[0].role.value == "user"
    assert msgs[1].role.value == "assistant"


def test_append_tool_calls(conv_manager, conversation):
    response = make_tool_response("call_1", "search")
    conv_manager.append_user("Search please")
    conv_manager.append_tool_calls(response)
    
    msgs = conversation.messages()
    assert len(msgs) == 2
    assert msgs[1].role.value == "assistant"
    assert msgs[1].tool_calls is not None
    assert msgs[1].tool_calls[0].id == "call_1"


def test_append_tool_result_success(conv_manager, conversation):
    response = make_tool_response("call_1", "search")
    conv_manager.append_tool_calls(response)
    
    result = ToolResult(call_id="call_1", status=ToolStatus.SUCCESS, output="Found data")
    conv_manager.append_tool_result(response.tool_calls[0], result)
    
    msgs = conversation.messages()
    assert len(msgs) == 2
    assert msgs[1].role.value == "tool"
    assert msgs[1].content == "Found data"
    assert msgs[1].metadata.get("tool_call_id") == "call_1"
    assert msgs[1].metadata.get("name") == "search"


def test_append_tool_result_empty_output(conv_manager, conversation):
    response = make_tool_response("call_1", "search")
    conv_manager.append_tool_calls(response)
    
    result = ToolResult(call_id="call_1", status=ToolStatus.SUCCESS, output=None)
    conv_manager.append_tool_result(response.tool_calls[0], result)
    
    msgs = conversation.messages()
    # FIX: Assert the placeholder string instead of empty string
    assert msgs[1].content == "Tool executed successfully with no output."


def test_append_tool_result_failure(conv_manager, conversation):
    response = make_tool_response("call_1", "search")
    conv_manager.append_tool_calls(response)
    
    result = ToolResult(call_id="call_1", status=ToolStatus.FAILED, error="API Down")
    conv_manager.append_tool_result(response.tool_calls[0], result)
    
    msgs = conversation.messages()
    assert "Error executing tool 'search': API Down" in msgs[1].content