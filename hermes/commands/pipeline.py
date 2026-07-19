"""
===============================================================================
Hermes Command Pipeline

Coordinates command parsing and execution.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.commands.command import Command
from hermes.commands.executor import CommandExecutor
from hermes.commands.parser import CommandParser
from hermes.commands.registry import CommandRegistry
from hermes.commands.result import CommandResult


class CommandPipeline:
    """
    Complete command execution pipeline.

    Text
        ↓
    Parser
        ↓
    Command
        ↓
    Executor
        ↓
    Result
    """

    def __init__(
        self,
        registry: CommandRegistry,
    ) -> None:

        self.parser = CommandParser()

        self.executor = CommandExecutor(
            registry,
        )

    # ------------------------------------------------------------------

    def execute(
        self,
        text: str,
    ) -> CommandResult:

        command: Command = self.parser.parse(
            text,
        )

        return self.executor.execute(
            command,
        )
