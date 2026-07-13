"""
===============================================================================
Hermes Executive Engine

The Executive is the brain of Hermes.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.executive.analyzer import ExecutiveAnalyzer
from hermes.executive.planner import ExecutivePlanner
from hermes.executive.validator import ExecutiveValidator
from hermes.executive.decision import ExecutiveDecision


class ExecutiveEngine:
    """
    Top-level Executive.

    Pipeline:

        Prompt
            ↓
        Analyze
            ↓
        Validate
            ↓
        Plan
            ↓
        Decision
    """

    def __init__(self) -> None:

        self.analyzer = ExecutiveAnalyzer()

        self.validator = ExecutiveValidator()

        self.planner = ExecutivePlanner()

    # ------------------------------------------------------------------

    def process(
        self,
        prompt: str,
    ) -> ExecutiveDecision:

        context = self.analyzer.analyze(
            prompt,
        )

        self.validator.validate(
            context,
        )

        return self.planner.plan(
            context,
        )