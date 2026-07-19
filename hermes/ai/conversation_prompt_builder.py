"""
===============================================================================
Hermes Conversation Prompt Builder

Stateless service to assemble a Prompt from an AIConversation.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.ai.conversation import AIConversation
from hermes.ai.prompt import Prompt


class ConversationPromptBuilder:
    """
    Stateless utility to build a Prompt from a conversation.

    Configuration can be provided at construction time.
    """

    def __init__(
        self,
        trim_to: int | None = None,
        include_summary: bool = False,
        include_system: bool = True,
    ) -> None:
        """
        Initialize the PromptBuilder with optional configuration.

        Parameters
        ----------
        trim_to : int | None, optional
            Maximum number of messages to include (trims oldest first).
        include_summary : bool, default=False
            Whether to include conversation summary in the prompt.
        include_system : bool, default=True
            Whether to include system messages.
        """
        self._trim_to = trim_to
        self._include_summary = include_summary
        self._include_system = include_system

    def build(
        self,
        conversation: AIConversation,
        system: str | None = None,
    ) -> Prompt:
        """
        Build a Prompt from the conversation.

        Parameters
        ----------
        conversation : AIConversation
            The conversation to build the prompt from.
        system : str | None, optional
            Optional system instruction to prepend.

        Returns
        -------
        Prompt
            A new Prompt containing the conversation messages.
        """
        prompt = Prompt()

        # Add system instruction if provided
        if system:
            prompt.add_system(system)

        # Optionally add summary
        if self._include_summary and conversation.summary is not None:
            prompt.add_message(
                role="system",
                content=f"Conversation summary: {conversation.summary.content}",
            )

        # Get messages with optional limit
        messages = conversation.messages(limit=self._trim_to)

        for msg in messages:
            if not self._include_system and msg.role == "system":
                continue
            # Convert conversation message to prompt message using to_prompt_message()
            prompt.add_message(msg.to_prompt_message())

        return prompt

    def build_ephemeral(
        self,
        message: str,
        system: str | None = None,
    ) -> Prompt:
        """
        Build a Prompt from a single message (stateless chat).

        Parameters
        ----------
        message : str
            The user message.
        system : str | None, optional
            Optional system instruction.

        Returns
        -------
        Prompt
            A new Prompt.
        """
        prompt = Prompt()
        if system:
            prompt.add_system(system)
        prompt.add_user(message)
        return prompt
