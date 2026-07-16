"""
===============================================================================
Hermes Ranking Engine

Ranks candidate providers according to routing requirements.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from hermes.providers.schemas import ProviderInfo
from hermes.routing.requirements import RoutingRequirements


@dataclass(slots=True)
class RankedProvider:
    """
    Provider paired with a routing score.
    """

    provider: ProviderInfo

    score: int


class RankingEngine:
    """
    Scores providers.

    Current implementation is intentionally minimal.

    Future versions will score using:

    • capabilities
    • latency
    • quotas
    • health
    • pricing
    • user preferences
    • historical success rate
    """

    def rank(
        self,
        providers: list[ProviderInfo],
        requirements: RoutingRequirements,
    ) -> list[RankedProvider]:

        ranked: list[RankedProvider] = []

        for provider in providers:

            score = 100

            if not provider.enabled:
                score -= 1000

            ranked.append(
                RankedProvider(
                    provider=provider,
                    score=score,
                )
            )

        ranked.sort(
            key=lambda item: item.score,
            reverse=True,
        )

        return ranked