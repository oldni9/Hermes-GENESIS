"""
===============================================================================
Conversation Manager
===============================================================================

Dependencies:
    - hermes.ai.conversation
    - hermes.ai.response
    - hermes.ai.tool

Consumes:
    - AIConversation
    - AIResponse (ToolCalls)
    - ToolResult

Produces:
    - Mutations on AIConversation

Public API:
    - ConversationManager.append_user()
    - ConversationManager.append_assistant()
    - ConversationManager.append_tool_calls()
    - ConversationManager.append_tool_result()
===============================================================================
"""

from __future__ import annotations

from hermes.ai.conversation import AIConversation
from hermes.ai.response import AIResponse, ToolCall
from hermes.ai.tool import ToolResult


class ConversationManager:
    """
    Handles all mutations to the AIConversation during the agent loop.
    Ensures strict adherence to the OpenAI tool-calling message sequence.
    """

    def __init__(self, conversation: AIConversation) -> None:
        self._conversation = conversation

    @property
    def conversation(self) -> AIConversation:
        return self._conversation

    def append_system(self, content: str) -> None:
        """Append a system message if the conversation is empty."""
        if len(self._conversation) == 0:
            self._conversation.system(content)

    def append_user(self, content: str) -> None:
        """Append a user message."""
        self._conversation.add_user(content)

    def append_assistant(self, content: str) -> None:
        """Append a final assistant message."""
        self._conversation.add_assistant(content)

    def append_tool_calls(self, response: AIResponse) -> None:
        """
        Append the assistant message containing tool calls.
        """
        self._conversation.add_message(
            role="assistant",
            content=response.text() or "",
            tool_calls=response.tool_calls,
        )

    def append_tool_result(self, tool_call: ToolCall, result: ToolResult) -> None:
        """
        Append a tool result message.
        Handles formatting the ToolResult output into a string payload.
        """
        tool_name = tool_call.function.name if tool_call.function else "unknown"
        
        if result.success:
            output_str = str(result.output) if result.output is not None else ""
            # Hermes ConversationValidator rejects empty content. 
            # If a tool returns None or "", use a placeholder.
            if not output_str.strip():
                output_str = "Tool executed successfully with no output."
        else:
            output_str = f"Error executing tool '{tool_name}': {result.error}"
        
        self._conversation.add_message(
            role="tool",
            content=output_str,
            tool_call_id=tool_call.id,
            name=tool_name,
        )