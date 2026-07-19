"""
===============================================================================
Hermes Agent Session
===============================================================================
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from hermes.ai.conversation import AIConversation


class AgentSession:
    """
    Holds the conversation history and metadata for a single agent.
    """

    def __init__(self, conversation: Optional[AIConversation] = None) -> None:
        self._conversation = conversation if conversation is not None else AIConversation(title="Agent Session")
        self._metadata: Dict[str, Any] = {}

    @property
    def conversation(self) -> AIConversation:
        return self._conversation

    @property
    def metadata(self) -> Dict[str, Any]:
        return self._metadata