"""
===============================================================================
Agent Request Builder (OpenAI Payload Serializer)
===============================================================================

Dependencies:
    - hermes.ai.conversation

Consumes:
    - AIConversation

Produces:
    - list[dict] (OpenAI-compatible message format)

Public API:
    - RequestBuilder.build()

NOTE:
This builder intentionally bypasses the Hermes Prompt system (Prompt, PromptMessage).
The Prompt system is designed for text-only representations and currently lacks
the fields required for tool-calling (e.g., tool_calls, tool_call_id).
Bypassing it ensures the Agent Executor can strictly adhere to the OpenAI
tool-calling wire format without polluting the text-prompting abstractions.

TODO:
Replace this serializer with the future ConversationSerializer
once Hermes introduces a provider-neutral chat serialization layer.
===============================================================================
"""

from __future__ import annotations

from typing import Any, List, Optional

from hermes.ai.conversation import AIConversation


class RequestBuilder:
    """
    Stateless utility to serialize an AIConversation into a list of 
    OpenAI-compatible message dictionaries.
    """

    @staticmethod
    def build(
        conversation: AIConversation, 
        transient_messages: Optional[List[dict[str, Any]]] = None
    ) -> List[dict[str, Any]]:
        """
        Serialize conversation history into provider-ready dictionaries.
        
        :param transient_messages: Optional list of messages to append temporarily 
                                    for the current request (e.g., retry feedback) 
                                    without mutating the AIConversation.
        """
        messages: List[dict[str, Any]] = []

        for msg in conversation.messages():
            if msg.deleted:
                continue

            role = msg.role.value if hasattr(msg.role, "value") else str(msg.role)
            
            entry: dict[str, Any] = {
                "role": role,
                "content": msg.content,
            }

            name = msg.metadata.get("name")
            if name:
                entry["name"] = name
                
            tool_call_id = msg.metadata.get("tool_call_id")
            if tool_call_id:
                entry["tool_call_id"] = tool_call_id
                
            if msg.tool_calls:
                entry["tool_calls"] = [tc.to_dict() for tc in msg.tool_calls]

            messages.append(entry)

        # Append transient messages at the end
        if transient_messages:
            messages.extend(transient_messages)

        return messages