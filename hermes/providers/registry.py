"""
===============================================================================
Hermes Provider Registry

Stores every provider discovered by the ProviderLoader.

The registry owns ONLY ProviderInfo objects.
It never creates clients or performs API calls.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from typing import Iterable

from hermes.providers.schemas import ProviderInfo


class ProviderRegistry:
    """
    Central metadata registry for all providers.
    """

    def __init__(self) -> None:
        self._providers: dict[str, ProviderInfo] = {}

    # ------------------------------------------------------------------

    def register(
        self,
        provider: ProviderInfo,
    ) -> None:
        """
        Register or replace a provider.
        """
        self._providers[provider.name.lower()] = provider

    # ------------------------------------------------------------------

    def unregister(
        self,
        name: str,
    ) -> None:
        """
        Remove a provider.
        """
        self._providers.pop(name.lower(), None)

    # ------------------------------------------------------------------

    def get(
        self,
        name: str,
    ) -> ProviderInfo:
        """
        Return a provider by name.

        Raises KeyError if missing.
        """
        return self._providers[name.lower()]

    # ------------------------------------------------------------------

    def exists(
        self,
        name: str,
    ) -> bool:
        """
        Check whether a provider exists.
        """
        return name.lower() in self._providers

    # ------------------------------------------------------------------

    def providers(self) -> list[ProviderInfo]:
        """
        Return all registered providers.
        """
        return list(self._providers.values())

    # ------------------------------------------------------------------

    def names(self) -> list[str]:
        """
        Return provider names.
        """
        return list(self._providers.keys())

    # ------------------------------------------------------------------

    def clear(self) -> None:
        """
        Remove every provider.
        """
        self._providers.clear()

    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self._providers)

    # ------------------------------------------------------------------

    def __contains__(
        self,
        name: str,
    ) -> bool:
        return self.exists(name)

    # ------------------------------------------------------------------

    def __iter__(self) -> Iterable[ProviderInfo]:
        return iter(self._providers.values())
