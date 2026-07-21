"""
===============================================================================
Agent Tool Result Serializer
===============================================================================

Dependencies:
    - hermes.ai.response
    - hermes.ai.tool

Consumes:
    - ToolCall
    - ToolResult

Produces:
    - str (formatted output)

Public API:
    - ToolResultSerializer
===============================================================================
"""

from __future__ import annotations

from hermes.ai.response import ToolCall
from hermes.ai.tool import ToolResult


class ToolResultSerializer:
    """
    Stateless utility to serialize ToolResult objects into conversation strings.
    Keeps serialization logic out of the orchestration loop and ConversationState.
    """

    @staticmethod
    def serialize(tool_call: ToolCall, result: ToolResult) -> str:
        """
        Convert a ToolResult into a string payload for the AIConversation.
        """
        tool_name = tool_call.function.name if tool_call.function else "unknown"
        
        if result is None:
            return "Error: Tool execution result missing."
        elif result.success:
            return str(result.output) if result.output is not None else ""
        else:
            return f"Error executing tool '{tool_name}': {result.error}"