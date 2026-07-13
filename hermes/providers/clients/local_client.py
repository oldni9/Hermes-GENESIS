"""
===============================================================================
Hermes Local Client

LM Studio / Ollama

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.providers.clients.base_client import BaseProviderClient
from hermes.providers.request import ProviderRequest
from hermes.providers.result import ProviderResult


class LocalClient(BaseProviderClient):

    @property
    def provider_name(self) -> str:

        return "Local"

    # -------------------------------------------------------------

    def generate(
        self,
        request: ProviderRequest,
    ) -> ProviderResult:

        return ProviderResult(

            success=True,

            text=f"[Local Placeholder] {request.prompt}",

        )