"""
===============================================================================
Hermes Executive Planner

Creates the initial execution objective.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.executive.context import ExecutiveContext
from hermes.executive.decision import ExecutiveDecision


class ExecutivePlanner:
    """
    Converts analyzed context into
    an ExecutiveDecision.
    """

    def plan(
        self,
        context: ExecutiveContext,
    ) -> ExecutiveDecision:
        """
        Build the first executive decision.
        """

        return ExecutiveDecision(
            prompt=context.prompt,
            action="chat",
            confidence=1.0,
        )