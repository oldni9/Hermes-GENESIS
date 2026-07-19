"""
===============================================================================
Hermes Provider Dispatcher

Dispatches provider requests through ClientFactory.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.providers.clients import ClientFactory
from hermes.providers.provider import Provider
from hermes.providers.request import ProviderRequest
from hermes.providers.result import ProviderResult


class ProviderDispatcher:
    """
    Executes requests using provider clients.

    The dispatcher knows nothing about Groq,
    Gemini, Ollama, LM Studio, etc.

    ClientFactory decides which implementation
    should be instantiated.
    """

    def __init__(
        self,
    ) -> None:

        self.factory = ClientFactory()

    # ------------------------------------------------------------------

    def dispatch(
        self,
        provider: Provider,
        request: ProviderRequest,
    ) -> ProviderResult:

        client = self.factory.create(
            provider,
        )

        return client.generate(
            request,
        )
