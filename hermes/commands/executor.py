"""
===============================================================================
Hermes Command Executor

Executes parsed commands through registered runtime subsystems.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.commands.command import Command
from hermes.commands.registry import CommandRegistry
from hermes.commands.result import CommandResult
from hermes.commands.base import BaseCommandHandler


class CommandExecutor:
    """
    Executes runtime commands.

    Receives a Command object,
    locates the proper subsystem,
    executes it,
    returns CommandResult.
    """

    def __init__(
        self,
        registry: CommandRegistry,
    ) -> None:

        self.registry = registry

    # ------------------------------------------------------------------

    def execute(
        self,
        command: Command,
    ) -> CommandResult:

        if not command.subsystem:

            return CommandResult(
                success=False,
                message="No subsystem selected.",
            )

        if not self.registry.exists(
            command.subsystem,
        ):

            return CommandResult(
                success=False,
                message=f"Subsystem '{command.subsystem}' not registered.",
            )

        handler: BaseCommandHandler = self.registry.get(
            command.subsystem,
        )

        return handler.execute(
            command,
        )
