"""
===============================================================================
Agent Context Factory
===============================================================================

Dependencies:
    - hermes.ai.conversation
    - hermes.ai.tool

Consumes:
    - AIConversation

Produces:
    - ToolContext

Public API:
    - AgentContextFactory

TODO:
    - Add tracing and telemetry spans to the context.
    - Add cancellation tokens for cooperative tool cancellation.
===============================================================================
"""

from __future__ import annotations

from hermes.ai.conversation import AIConversation
from hermes.ai.tool import ToolContext


class AgentContextFactory:
    """
    Factory responsible for constructing the ToolContext for each tool batch.
    """

    def build(self, conversation: AIConversation) -> ToolContext:
        """
        Build a ToolContext containing the current execution state.
        """
        return ToolContext(conversation=conversation)