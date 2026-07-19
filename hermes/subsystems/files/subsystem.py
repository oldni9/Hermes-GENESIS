"""
===============================================================================
Hermes Files Subsystem
===============================================================================
"""

from __future__ import annotations

from hermes.commands.command import Command
from hermes.commands.result import CommandResult

from hermes.subsystems import BaseSubsystem

from .metadata import FILES_METADATA
from .metadata import FILES_CAPABILITIES
from .state import FilesState


class FilesSubsystem(BaseSubsystem):

    def __init__(self):

        self.metadata = FILES_METADATA

        self.capabilities = FILES_CAPABILITIES

        self.state = FilesState()

        self.operations = FileOperations()

        self.search = FileSearch()

        self.metadata_service = FileMetadata()

        self.safety = FileSafety()

        self.archive = FileArchive()

        self.index = FileIndex()

        self.watcher = FileWatcher()

    # ---------------------------------------------------------

    @property
    def name(self) -> str:

        return self.metadata.name

    # ---------------------------------------------------------

    def startup(self) -> None:

        self.state.loaded = True

    # ---------------------------------------------------------

    def shutdown(self) -> None:

        self.state.loaded = False

    # ---------------------------------------------------------

    def execute(
        self,
        command: Command,
    ) -> CommandResult:

        self.state.last_operation = command.action

        return CommandResult(
            success=True,
            message=f"Files subsystem received '{command.action}'.",
        )
