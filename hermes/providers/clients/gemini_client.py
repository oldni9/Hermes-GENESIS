"""
===============================================================================
Hermes Gemini Client

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

import google.generativeai as genai

from hermes.providers.clients.base_client import BaseProviderClient
from hermes.providers.config import ProviderConfig
from hermes.providers.request import ProviderRequest
from hermes.providers.result import ProviderResult


class GeminiClient(BaseProviderClient):
    """
    Google Gemini Provider Client.
    """

    def __init__(
        self,
        config: ProviderConfig,
    ) -> None:

        super().__init__(config.name)

        self.config = config

        genai.configure(
            api_key=config.api_key,
        )

        self.model = genai.GenerativeModel(
            config.default_model,
        )

    # ------------------------------------------------------------------

    def generate(
        self,
        request: ProviderRequest,
    ) -> ProviderResult:

        response = self.model.generate_content(
            request.prompt,
        )

        return ProviderResult(
            success=True,
            text=response.text,
            raw=response,
        )