"""
===============================================================================
Hermes Provider Dispatcher

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.providers.clients import ProviderClientRegistry
from hermes.providers.enums import ProviderType
from hermes.providers.request import ProviderRequest
from hermes.providers.result import ProviderResult


class ProviderDispatcher:
    """
    Executes requests using registered provider clients.
    """

    def __init__(self) -> None:

        self.registry = ProviderClientRegistry()

    # ------------------------------------------------------------------

    def execute(
        self,
        provider: ProviderType,
        request: ProviderRequest,
    ) -> ProviderResult:

        client = self.registry.get(
            provider,
        )

        if client is None:

            raise RuntimeError(
                f"No client registered for {provider}"
            )

        return client.generate(
            request,
        )