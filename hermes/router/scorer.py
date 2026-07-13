"""
===============================================================================
Hermes Route Scorer
===============================================================================
"""

from __future__ import annotations

from hermes.router.score import RouteScore


class RouteScorer:
    """
    Temporary scoring engine.

    Future versions will combine:

    - latency
    - cost
    - health
    - preference
    - policy
    """

    def score(
        self,
        candidate: RouteScore,
    ) -> float:

        return candidate.score