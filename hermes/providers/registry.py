"""
===============================================================================
Hermes Provider Registry
===============================================================================
"""

from __future__ import annotations

from hermes.providers.enums import ProviderType
from hermes.providers.provider import Provider


class ProviderRegistry:

    def __init__(self) -> None:

        self._providers: dict[
            ProviderType,
            Provider,
        ] = {}

    # ---------------------------------------------------------

    def register(
        self,
        provider: Provider,
    ) -> None:

        self._providers[
            provider.name
        ] = provider

    # ---------------------------------------------------------

    def get(
        self,
        provider: ProviderType,
    ) -> Provider | None:

        return self._providers.get(
            provider,
        )

    # ---------------------------------------------------------

    def all(
        self,
    ) -> list[Provider]:

        return list(
            self._providers.values()
        )