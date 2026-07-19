# hermes/providers/resolver.py

"""
===============================================================================
Hermes Provider Resolver

Resolves which provider should execute a capability.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.providers.exceptions import (
    ProviderDisabled,
    ProviderNotFound,
)
from hermes.providers.provider import Provider
from hermes.providers.registry import ProviderRegistry


class ProviderResolver:
    """
    Resolves providers from the registry.
    """

    def __init__(
        self,
        registry: ProviderRegistry,
    ) -> None:

        self._registry = registry

    # ------------------------------------------------------------------

    def resolve(
        self,
        name: str,
    ) -> Provider:
        """
        Resolve a provider by name.
        """

        provider = self._registry.get(name)

        if provider is None:

            raise ProviderNotFound(f"Provider '{name}' was not found.")

        if not provider.enabled:

            raise ProviderDisabled(f"Provider '{name}' is disabled.")

        return provider
