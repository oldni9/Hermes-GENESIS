"""
===============================================================================
Hermes Base Provider Client

Base interface implemented by every provider client.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from hermes.providers.request import ProviderRequest
from hermes.providers.result import ProviderResult


class BaseProviderClient(ABC):
    """
    Base class for every provider implementation.
    """

    def __init__(
        self,
        provider_name: str,
    ) -> None:

        self._provider_name = provider_name

    # ------------------------------------------------------------------

    @property
    def provider_name(
        self,
    ) -> str:

        return self._provider_name

    # ------------------------------------------------------------------

    @abstractmethod
    def generate(
        self,
        request: ProviderRequest,
    ) -> ProviderResult:
        """
        Standard synchronous text generation.
        """

    # ------------------------------------------------------------------

    def stream(
        self,
        request: ProviderRequest,
    ):
        raise NotImplementedError(
            f"{self.provider_name} does not support streaming."
        )

    # ------------------------------------------------------------------

    def embeddings(
        self,
        request: ProviderRequest,
    ):
        raise NotImplementedError(
            f"{self.provider_name} does not support embeddings."
        )

    # ------------------------------------------------------------------

    def image_generation(
        self,
        request: ProviderRequest,
    ):
        raise NotImplementedError(
            f"{self.provider_name} does not support image generation."
        )

    # ------------------------------------------------------------------

    def speech(
        self,
        request: ProviderRequest,
    ):
        raise NotImplementedError(
            f"{self.provider_name} does not support speech."
        )

    # ------------------------------------------------------------------

    def transcribe(
        self,
        request: ProviderRequest,
    ):
        raise NotImplementedError(
            f"{self.provider_name} does not support transcription."
        )

    # ------------------------------------------------------------------

    def live(
        self,
        request: ProviderRequest,
    ):
        raise NotImplementedError(
            f"{self.provider_name} does not support live sessions."
        )

    # ------------------------------------------------------------------

    def list_models(
        self,
    ):
        raise NotImplementedError(
            f"{self.provider_name} cannot enumerate models."
        )

    # ------------------------------------------------------------------

    def health_check(
        self,
    ) -> bool:

        return True