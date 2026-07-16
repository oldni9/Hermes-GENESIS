"""
===============================================================================
Hermes Base Command Handler

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from hermes.commands.command import Command


class BaseCommandHandler(ABC):
    """
    Base interface for every Hermes subsystem.

    Files

    Music

    Mail

    Dashboard

    IDE

    Runtime

    all inherit this.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Subsystem name.
        """

    @abstractmethod
    def execute(
        self,
        command: Command,
    ):
        """
        Execute command.
        """