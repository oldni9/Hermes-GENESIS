"""
===============================================================================
Hermes Integration Registry

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.integration.history import IntegrationHistory


class IntegrationRegistry:

    def __init__(self) -> None:

        self._history: list[IntegrationHistory] = []

    # ------------------------------------------------------------------

    def add(
        self,
        history: IntegrationHistory,
    ) -> None:

        self._history.append(history)

    # ------------------------------------------------------------------

    def all(
        self,
    ) -> list[IntegrationHistory]:

        return list(self._history)

    # ------------------------------------------------------------------

    def clear(
        self,
    ) -> None:

        self._history.clear()
