"""
===============================================================================
Hermes Provider Client Registry

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.providers.enums import ProviderType

from hermes.providers.clients.base_client import BaseProviderClient


class ProviderClientRegistry:
    """
    Stores provider client implementations.

    Dispatcher retrieves clients from here instead
    of using if/else chains.
    """

    def __init__(self) -> None:

        self._clients: dict[
            ProviderType,
            BaseProviderClient,
        ] = {}

    # -------------------------------------------------------------

    def register(
        self,
        provider: ProviderType,
        client: BaseProviderClient,
    ) -> None:

        self._clients[
            provider
        ] = client

    # -------------------------------------------------------------

    def get(
        self,
        provider: ProviderType,
    ) -> BaseProviderClient | None:

        return self._clients.get(
            provider,
        )

    # -------------------------------------------------------------

    def all(self):

        return list(
            self._clients.values()
        )