"""
===============================================================================
Hermes Candidate Builder

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.models.model import Model
from hermes.providers.registry import ProviderRegistry
from hermes.router.score import RouteScore


class CandidateBuilder:
    """
    Converts Models into RouteScore candidates.

    It never executes providers.

    It never creates ProviderManager.

    It only converts Model -> Provider -> RouteScore.
    """

    def __init__(
        self,
        registry: ProviderRegistry,
    ) -> None:

        self.registry = registry

    # ------------------------------------------------------------------

    def build(
        self,
        models: list[Model],
    ) -> list[RouteScore]:

        candidates: list[RouteScore] = []

        for model in models:

            provider = self.registry.get(
                model.provider,
            )

            if provider is None:
                continue

            candidates.append(

                RouteScore(

                    model=model,

                    provider=provider,

                    score=float(
                        model.priority,
                    ),

                )

            )

        return candidates