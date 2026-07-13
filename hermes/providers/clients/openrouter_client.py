"""
===============================================================================
Hermes OpenRouter Client
===============================================================================
"""

from __future__ import annotations

from hermes.providers.clients.openai_compatible import OpenAICompatibleClient


class OpenRouterClient(OpenAICompatibleClient):

    @property
    def provider_name(self) -> str:

        return "OpenRouter"