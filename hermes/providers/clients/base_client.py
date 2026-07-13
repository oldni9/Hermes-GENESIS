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

    Every provider must implement the same interface so
    Hermes can dispatch requests without caring about the
    underlying API.
    """

    def __init__(self) -> None:
        super().__init__()

    # ------------------------------------------------------------------

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        Human-readable provider name.
        """

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
        """
        Streaming generation.

        Override if supported.
        """
        raise NotImplementedError(
            f"{self.provider_name} does not support streaming."
        )

    # ------------------------------------------------------------------

    def embeddings(
        self,
        request: ProviderRequest,
    ):
        """
        Embedding generation.

        Override if supported.
        """
        raise NotImplementedError(
            f"{self.provider_name} does not support embeddings."
        )

    # ------------------------------------------------------------------

    def image_generation(
        self,
        request: ProviderRequest,
    ):
        """
        Image generation.

        Override if supported.
        """
        raise NotImplementedError(
            f"{self.provider_name} does not support image generation."
        )

    # ------------------------------------------------------------------

    def speech(
        self,
        request: ProviderRequest,
    ):
        """
        Text-to-Speech.

        Override if supported.
        """
        raise NotImplementedError(
            f"{self.provider_name} does not support speech."
        )

    # ------------------------------------------------------------------

    def transcribe(
        self,
        request: ProviderRequest,
    ):
        """
        Speech-to-Text.

        Override if supported.
        """
        raise NotImplementedError(
            f"{self.provider_name} does not support transcription."
        )

    # ------------------------------------------------------------------

    def live(
        self,
        request: ProviderRequest,
    ):
        """
        Low-latency realtime session.

        Used by providers like Gemini Live.

        Override if supported.
        """
        raise NotImplementedError(
            f"{self.provider_name} does not support live sessions."
        )

    # ------------------------------------------------------------------

    def list_models(self):
        """
        Return available models.

        Override if supported.
        """
        raise NotImplementedError(
            f"{self.provider_name} cannot enumerate models."
        )

    # ------------------------------------------------------------------

    def health_check(self) -> bool:
        """
        Simple connectivity test.

        Override in concrete providers.
        """
        return True