"""
===============================================================================
Hermes Executive Registry

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.executive.decision import ExecutiveDecision


class ExecutiveRegistry:
    """
    Stores executive decisions.
    """

    def __init__(self) -> None:

        self._decisions: list[ExecutiveDecision] = []

    # --------------------------------------------------------------

    def add(
        self,
        decision: ExecutiveDecision,
    ) -> None:

        self._decisions.append(decision)

    # --------------------------------------------------------------

    def all(
        self,
    ) -> list[ExecutiveDecision]:

        return list(self._decisions)

    # --------------------------------------------------------------

    def clear(
        self,
    ) -> None:

        self._decisions.clear()
