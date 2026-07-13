"""
===============================================================================
Hermes Genesis Interfaces
===============================================================================

Abstract contracts shared across Hermes.

===============================================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class Component(ABC):
    """
    Base contract for every Hermes subsystem.
    """

    @abstractmethod
    def initialize(self) -> None:
        ...

    @abstractmethod
    def shutdown(self) -> None:
        ...