"""
===============================================================================
Hermes Gemini Client

Native Google Gemini SDK implementation.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.providers.clients.base_client import BaseProviderClient
from hermes.providers.request import ProviderRequest
from hermes.providers.result import ProviderResult


class GeminiClient(BaseProviderClient):
    """
    Native Gemini implementation.

    Future implementation will use:

        google-genai SDK

    NOT raw HTTP requests.
    """

    def __init__(
        self,
        api_key: str | None = None,
    ) -> None:

        self.api_key = api_key

        #
        # Future:
        #
        # from google import genai
        # self.client = genai.Client(api_key=...)
        #

    # ------------------------------------------------------------------

    @property
    def provider_name(self) -> str:

        return "Gemini"

    # ------------------------------------------------------------------

    def generate(
        self,
        request: ProviderRequest,
    ) -> ProviderResult:

        #
        # SDK implementation comes later.
        #

        return ProviderResult(

            success=True,

            text=f"[Gemini Placeholder] {request.prompt}",

        )

    # ------------------------------------------------------------------

    def stream(
        self,
        request: ProviderRequest,
    ):

        raise NotImplementedError()

    # ------------------------------------------------------------------

    def live(
        self,
        request: ProviderRequest,
    ):

        raise NotImplementedError()

    # ------------------------------------------------------------------

    def list_models(self):

        raise NotImplementedError()

    # ------------------------------------------------------------------

    def health_check(self) -> bool:

        return True