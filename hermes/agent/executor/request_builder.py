"""
===============================================================================
Agent Request Builder
===============================================================================

Dependencies:
    - hermes.ai.conversation
    - hermes.ai.request

Consumes:
    - AIConversation

Produces:
    - AIRequest

Public API:
    - RequestBuilder
===============================================================================
"""

from __future__ import annotations

from hermes.ai.conversation import AIConversation
from hermes.ai.request import AIRequest


class RequestBuilder:
    """
    Utility to construct an AIRequest from conversation history.
    Instantiated as a class to allow future state (e.g., token budgeting, provider quirks).
    """

    def __init__(self, provider: str, model: str) -> None:
        self._provider = provider
        self._model = model

    @property
    def provider(self) -> str:
        return self._provider

    @property
    def model(self) -> str:
        return self._model

    def build(self, conversation: AIConversation) -> AIRequest:
        """Build an AIRequest from the conversation history."""
        message_dicts = [msg.to_dict() for msg in conversation.messages()]
        
        return AIRequest(
            prompt="",
            input=None,
            provider=self._provider,
            model=self._model,
            task="chat",
            options={"messages": message_dicts},
            metadata={},
        )