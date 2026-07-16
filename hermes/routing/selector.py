"""
===============================================================================
Hermes Provider Selector

Chooses the final provider after ranking.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.providers.schemas import ProviderInfo

from hermes.routing.ranking import RankedProvider


class ProviderSelector:
    """
    Selects the highest-ranked provider.

    Future versions will support:

    • failover
    • provider health
    • quota exhaustion
    • retry chains
    • user preferences
    • runtime policies
    """

    def select(
        self,
        ranked: list[RankedProvider],
    ) -> ProviderInfo:

        if not ranked:

            raise RuntimeError(
                "No providers available."
            )

        return ranked[0].provider