"""
===============================================================================
Hermes Reasoning Analyzer

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.executive.decision import ExecutiveDecision
from hermes.reasoning.context import ReasoningContext


class ReasoningAnalyzer:
    """
    Converts Executive decisions into
    reasoning contexts.
    """

    def analyze(
        self,
        decision: ExecutiveDecision,
    ) -> ReasoningContext:

        return ReasoningContext(
            prompt=decision.action,
            objective=decision.action,
        )