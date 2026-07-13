"""
===============================================================================
Hermes Model Selector
===============================================================================
"""

from __future__ import annotations

from hermes.router.score import RouteScore
from hermes.router.scorer import RouteScorer


class ModelSelector:
    """
    Selects the highest-scoring routing candidate.
    """

    def __init__(self):

        self.scorer = RouteScorer()

    # ------------------------------------------------------------------

    def select(
        self,
        candidates: list[RouteScore],
    ) -> RouteScore:

        return max(

            candidates,

            key=lambda candidate: self.scorer.score(
                candidate,
            ),

        )