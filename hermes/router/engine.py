"""
===============================================================================
Hermes Routing Engine

Central routing pipeline.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.providers.registry import ProviderRegistry
from hermes.providers.schemas import ProviderInfo

from hermes.routing.requirements import RequirementAnalyzer
from hermes.routing.ranking import RankingEngine
from hermes.routing.selector import ProviderSelector


class RoutingEngine:
    """
    Main routing pipeline.

    Pipeline:

        Analyze
            ↓
        Rank
            ↓
        Select
    """

    def __init__(
        self,
        registry: ProviderRegistry,
    ) -> None:

        self.registry = registry

        self.analyzer = RequirementAnalyzer()

        self.ranker = RankingEngine()

        self.selector = ProviderSelector()

    # ------------------------------------------------------------------

    def route(
        self,
    ) -> ProviderInfo:

        requirements = self.analyzer.analyze()

        providers = self.registry.providers()

        ranked = self.ranker.rank(
            providers,
            requirements,
        )

        return self.selector.select(
            ranked,
        )
