"""
===============================================================================
Agent Context Factory
===============================================================================

Dependencies:
    - typing
    - hermes.ai.conversation
    - hermes.ai.tool
    - hermes.workspace.workspace

Consumes:
    - AIConversation
    - Workspace (Optional)

Produces:
    - ToolContext

Public API:
    - AgentContextFactory
===============================================================================
"""

from __future__ import annotations

from typing import Optional

from hermes.ai.conversation import AIConversation
from hermes.ai.tool import ToolContext
from hermes.workspace.workspace import Workspace


class AgentContextFactory:
    """
    Factory responsible for constructing the ToolContext for each tool batch.
    Keeps runtime state construction out of the orchestration loop.
    """

    def build(
        self, 
        conversation: AIConversation, 
        workspace: Optional[Workspace] = None
    ) -> ToolContext:
        """
        Build a ToolContext containing the current execution state.
        """
        # Future-proofing: pass workspace if available so tools can access 
        # filesystem, memory, sandbox, etc.
        return ToolContext(
            conversation=conversation,
            runtime=workspace
        )