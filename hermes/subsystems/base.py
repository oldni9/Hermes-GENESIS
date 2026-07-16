"""
===============================================================================
Hermes Subsystem Base
===============================================================================
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from hermes.commands.command import Command
from hermes.commands.result import CommandResult


class BaseSubsystem(ABC):
    """
    Base class for every Hermes subsystem.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def startup(self) -> None:
        ...

    @abstractmethod
    def shutdown(self) -> None:
        ...

    @abstractmethod
    def execute(
        self,
        command: Command,
    ) -> CommandResult:
        ...