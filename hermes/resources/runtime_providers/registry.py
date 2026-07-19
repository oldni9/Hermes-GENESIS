"""
===============================================================================
Provider Registry
===============================================================================
"""

from __future__ import annotations

from hermes.providers.provider import Provider


class ProviderRegistry:

    def __init__(self) -> None:

        self._providers: dict[str, Provider] = {}

    def register(
        self,
        provider: Provider,
    ) -> None:

        self._providers[provider.name] = provider

    def get(
        self,
        name: str,
    ) -> Provider | None:

        return self._providers.get(name)

    def all(
        self,
    ) -> list[Provider]:

        return list(self._providers.values())
