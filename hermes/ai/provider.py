"""
===============================================================================
Hermes AI Provider

Base provider for every AI capability.

Examples

    Gemini OCR
    PaddleOCR
    Tesseract
    Florence2
    Qwen-VL
    Whisper
    CLIP

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from hermes.ai.context import AIContext
from hermes.ai.metadata import AIMetadata
from hermes.ai.request import AIRequest
from hermes.ai.response import AIResponse


class BaseAIProvider(ABC):
    """
    Base class for every Hermes AI provider.
    """

    def __init__(self) -> None:

        self._started = False

    # ------------------------------------------------------------------

    @property
    @abstractmethod
    def metadata(self) -> AIMetadata:
        """
        Provider metadata.
        """
        ...

    # ------------------------------------------------------------------

    @property
    def name(self) -> str:

        return self.metadata.name

    # ------------------------------------------------------------------

    @property
    def started(self) -> bool:

        return self._started

    # ------------------------------------------------------------------

    def startup(self) -> None:

        self._started = True

    # ------------------------------------------------------------------

    def shutdown(self) -> None:

        self._started = False

    # ------------------------------------------------------------------

    def supports(
        self,
        capability: str,
    ) -> bool:

        return self.metadata.supports(capability)

    # ------------------------------------------------------------------

    def health(self) -> bool:

        return self._started

    # ------------------------------------------------------------------

    def batch_execute(
        self,
        requests: list[AIRequest],
        context: AIContext | None = None,
    ) -> list[AIResponse]:

        responses: list[AIResponse] = []

        for request in requests:

            responses.append(
                self.execute(
                    request,
                    context,
                )
            )

        return responses

    # ------------------------------------------------------------------

    @abstractmethod
    def execute(
        self,
        request: AIRequest,
        context: AIContext | None = None,
    ) -> AIResponse:
        """
        Execute one AI request.
        """
        ...
