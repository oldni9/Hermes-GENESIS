"""
===============================================================================
Hermes Subsystem Manager
===============================================================================
"""

from __future__ import annotations

from hermes.commands.command import Command
from hermes.commands.result import CommandResult
from hermes.subsystems.registry import SubsystemRegistry


class SubsystemManager:

    def __init__(
        self,
        registry: SubsystemRegistry,
    ) -> None:

        self.registry = registry

    # ---------------------------------------------------------

    def startup_all(self):

        for subsystem in self.registry.values():

            subsystem.startup()

    # ---------------------------------------------------------

    def shutdown_all(self):

        for subsystem in self.registry.values():

            subsystem.shutdown()

    # ---------------------------------------------------------

    def execute(
        self,
        command: Command,
    ) -> CommandResult:

        subsystem = self.registry.get(command.subsystem)

        if subsystem is None:

            return CommandResult(
                success=False,
                message=f"Subsystem '{command.subsystem}' not found.",
            )

        return subsystem.execute(command)
