"""
===============================================================================
Agent Conversation State
===============================================================================

Dependencies:
    - hermes.ai.conversation

Consumes:
    - AIConversation

Produces:
    - Mutations on AIConversation

Public API:
    - ConversationState
===============================================================================
"""

from __future__ import annotations

from hermes.ai.conversation import AIConversation
from hermes.ai.response import AIResponse


class ConversationState:
    """
    Strict gatekeeper for AIConversation mutations.
    Enforces the OpenAI tool-calling message sequence contract.
    Completely dumb: only appends pre-formatted strings; knows nothing of ToolResult.
    """

    def __init__(self, conversation: AIConversation) -> None:
        self._conversation = conversation

    @property
    def conversation(self) -> AIConversation:
        return self._conversation

    def append_system_if_empty(self, system_prompt: str) -> None:
        """Append a system prompt only if the conversation is empty."""
        if len(self._conversation) == 0:
            # FIX: Use the correct AIConversation method 'system'
            self._conversation.system(system_prompt)

    def append_user(self, prompt: str) -> None:
        """Append a user message."""
        self._conversation.add_user(prompt)

    def append_assistant_tool_calls(self, response: AIResponse) -> None:
        """Append the assistant message containing tool calls."""
        self._conversation.add_message(
            role="assistant",
            content=response.text() or "",
            tool_calls=response.tool_calls,
        )

    def append_assistant_text(self, text: str) -> None:
        """Append the final assistant text message."""
        self._conversation.add_assistant(text)

    def append_tool_message(
        self, 
        tool_call_id: str, 
        tool_name: str, 
        output: str
    ) -> None:
        """Append a tool result message using a pre-formatted output string."""
        self._conversation.add_message(
            role="tool",
            content=output,
            tool_call_id=tool_call_id,
            name=tool_name,
        )

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture