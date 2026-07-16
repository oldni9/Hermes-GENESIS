"""
===============================================================================
Hermes Provider Client Registry

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.providers.clients.base_client import BaseProviderClient


class ProviderClientRegistry:
    """
    Stores instantiated provider clients.

    Dispatcher never imports provider classes directly.

    It simply asks this registry.
    """

    def __init__(self) -> None:

        self._clients: dict[str, BaseProviderClient] = {}

    # ------------------------------------------------------------------

    def register(
        self,
        client: BaseProviderClient,
    ) -> None:

        self._clients[client.provider_name] = client

    # ------------------------------------------------------------------

    def get(
        self,
        provider_name: str,
    ) -> BaseProviderClient:

        return self._clients[provider_name]

    # ------------------------------------------------------------------

    def exists(
        self,
        provider_name: str,
    ) -> bool:

        return provider_name in self._clients

    # ------------------------------------------------------------------

    def names(
        self,
    ) -> list[str]:

        return list(self._clients.keys())

    # ------------------------------------------------------------------

    def all(
        self,
    ) -> dict[str, BaseProviderClient]:

        return self._clients