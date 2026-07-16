"""
===============================================================================
Hermes Ollama Client
===============================================================================
"""

from __future__ import annotations

from hermes.providers.clients.openai_compatible import OpenAICompatibleClient
from hermes.providers.config import ProviderConfig


class OllamaClient(OpenAICompatibleClient):

    def __init__(
        self,
        config: ProviderConfig,
    ) -> None:

        super().__init__(config)