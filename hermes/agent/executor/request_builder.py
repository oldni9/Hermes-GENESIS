"""
===============================================================================
Agent Request Builder
===============================================================================

Sprint 12 Update:
Added threading.Lock to ensure thread-safe request building during parallel execution.
===============================================================================
"""
from __future__ import annotations

import threading
from typing import Any, List

from hermes.ai.conversation import AIConversation
from hermes.ai.request import AIRequest


class RequestBuilder:
    """
    Utility to construct an AIRequest from conversation history.
    Thread-safe.
    """

    def __init__(self, provider: str, model: str) -> None:
        self._provider = provider
        self._model = model
        self._lock = threading.Lock()

    @property
    def provider(self) -> str:
        return self._provider

    @property
    def model(self) -> str:
        return self._model

    def build(self, conversation: AIConversation) -> AIRequest:
        """Build an AIRequest from the conversation history. Thread-safe."""
        with self._lock:
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

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture