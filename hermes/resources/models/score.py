"""
===============================================================================
Hermes Runtime Model Score Engine

Computes scores for Runtime Models.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.resources.models.model import RuntimeModel


class ModelScoreEngine:
    """
    Computes a numeric score for Runtime Models.

    Genesis uses simple heuristics.

    Future versions will include:

        • Cost awareness
        • Latency history
        • Trust engine
        • Failure history
        • User preferences
        • Scheduler policies
        • Adaptive learning
    """

    # ------------------------------------------------------------------

    def score(
        self,
        model: RuntimeModel,
    ) -> float:
        """
        Compute a score for a model.

        Higher score = Better candidate.
        """

        score = 0.0

        # --------------------------------------------------------------
        # Enabled
        # --------------------------------------------------------------

        if model.enabled:
            score += 100.0

        # --------------------------------------------------------------
        # Context Window
        # --------------------------------------------------------------

        score += model.context_window / 10000

        # --------------------------------------------------------------
        # Cost
        # --------------------------------------------------------------

        score -= model.cost

        # --------------------------------------------------------------
        # Latency
        # --------------------------------------------------------------

        score -= model.latency / 1000

        return score

    # ------------------------------------------------------------------

    def compare(
        self,
        left: RuntimeModel,
        right: RuntimeModel,
    ) -> RuntimeModel:
        """
        Return the higher scoring model.
        """

        if self.score(left) >= self.score(right):
            return left

        return right