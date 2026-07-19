"""
===============================================================================
Hermes OpenAI Compatible Client

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from openai import OpenAI

from hermes.providers.clients.base_client import BaseProviderClient
from hermes.providers.config import ProviderConfig
from hermes.providers.request import ProviderRequest
from hermes.providers.result import ProviderResult


class OpenAICompatibleClient(BaseProviderClient):
    """
    Base implementation for every OpenAI-compatible provider.

    Examples:

        - Groq
        - OpenRouter
        - LM Studio
        - Ollama
        - Cloudflare
        - ZAI
        - Together
        - Fireworks
        - DeepSeek
    """

    def __init__(
        self,
        config: ProviderConfig,
    ) -> None:

        super().__init__(config.name)

        self.config = config

        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
        )

    # ------------------------------------------------------------------

    def generate(
        self,
        request: ProviderRequest,
    ) -> ProviderResult:

        response = self.client.chat.completions.create(
            model=self.config.default_model,
            messages=[
                {
                    "role": "user",
                    "content": request.prompt,
                }
            ],
        )

        return ProviderResult(
            success=True,
            text=response.choices[0].message.content,
            raw=response,
        )
