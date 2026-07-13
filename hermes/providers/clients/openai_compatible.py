"""
===============================================================================
Hermes OpenAI Compatible Client

Base class for providers exposing an OpenAI-compatible API.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.providers.clients.base_client import BaseProviderClient
from hermes.providers.request import ProviderRequest
from hermes.providers.result import ProviderResult


class OpenAICompatibleClient(BaseProviderClient):

    def __init__(
        self,
        base_url: str = "",
        api_key: str | None = None,
    ) -> None:

        self.base_url = base_url

        self.api_key = api_key

    # -------------------------------------------------------------

    @property
    def provider_name(self) -> str:

        return "OpenAI Compatible"

    # -------------------------------------------------------------

    def generate(
        self,
        request: ProviderRequest,
    ) -> ProviderResult:

        return ProviderResult(

            success=True,

            text=f"[OpenAI Compatible] {request.prompt}",

        )