"""
===============================================================================
Hermes Executive Analyzer

Analyzes user intent before reasoning begins.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.executive.context import ExecutiveContext


class ExecutiveAnalyzer:
    """
    First stage of the Executive.

    Responsible for understanding
    the user's request before planning.
    """

    def analyze(
        self,
        prompt: str,
    ) -> ExecutiveContext:

        context = ExecutiveContext()

        context.prompt = prompt

        context.objective = prompt.strip()

        return context