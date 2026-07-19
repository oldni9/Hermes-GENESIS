"""
===============================================================================
Hermes Scheduler Manager
===============================================================================

High-level Scheduler Runtime manager.

===============================================================================
"""

from __future__ import annotations

from pathlib import Path

from .loader import SchedulerLoader
from .policy import SchedulerPolicy
from .registry import SchedulerRegistry
from .validator import SchedulerValidator


class SchedulerManager:
    """
    Coordinates Scheduler Policies.
    """

    def __init__(self) -> None:

        self._registry = SchedulerRegistry()

        self._validator = SchedulerValidator()

        self._loader = SchedulerLoader()

    # ------------------------------------------------------------------

    def register(
        self,
        policy: SchedulerPolicy,
    ) -> None:

        self._validator.validate(policy)

        self._registry.register(policy)

    # ------------------------------------------------------------------

    def discover(
        self,
        directory: Path,
    ) -> None:

        policies = self._loader.load(directory)

        for policy in policies:

            self.register(policy)

    # ------------------------------------------------------------------

    def get(
        self,
        policy_id: str,
    ) -> SchedulerPolicy | None:

        return self._registry.get(policy_id)

    # ------------------------------------------------------------------

    def all(
        self,
    ) -> list[SchedulerPolicy]:

        return self._registry.all()

    # ------------------------------------------------------------------

    def unregister(
        self,
        policy_id: str,
    ) -> None:

        self._registry.unregister(policy_id)

    # ------------------------------------------------------------------

    def clear(
        self,
    ) -> None:

        self._registry.clear()
