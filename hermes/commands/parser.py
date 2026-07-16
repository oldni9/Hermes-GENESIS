"""
===============================================================================
Hermes Command Parser

Converts raw user input into canonical Command objects.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.commands.command import Command


class CommandParser:
    """
    Converts raw text into runtime commands.

    Later this class will use:
        • LLM structured output
        • Intent detection
        • Tool planning
        • Multi-command decomposition

    For now it simply wraps text.
    """

    # ------------------------------------------------------------------

    def parse(
        self,
        text: str,
    ) -> Command:

        return Command(
            text=text.strip(),
        )