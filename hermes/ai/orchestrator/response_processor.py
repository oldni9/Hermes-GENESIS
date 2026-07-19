"""
===============================================================================
Hermes AI Response Processor

Normalizes and processes provider responses.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

import time

from hermes.ai.response import AIResponse


class ResponseProcessor:
    """
    Normalizes and processes provider responses.
    Adds metadata, usage, latency, finish reason.
    """

    def process(
        self,
        raw_response: AIResponse,
        provider_name: str,
        model_name: str | None = None,
        start_time: float | None = None,
    ) -> AIResponse:
        """
        Process and normalize a provider response.

        Parameters
        ----------
        raw_response : AIResponse
            The raw response from the provider.
        provider_name : str
            The name of the provider.
        model_name : str | None, optional
            The model used.
        start_time : float | None, optional
            Start time for latency calculation.

        Returns
        -------
        AIResponse
            The normalized response (same instance, mutated).
        """
        # Set provider and model if not already set
        if not raw_response.provider:
            raw_response.provider = provider_name
        if model_name and not raw_response.model:
            raw_response.model = model_name

        # Calculate duration if not already set
        if raw_response.duration == 0.0 and start_time is not None:
            # Fallback to a microscopic float above 0 if processed instantly
            elapsed = max(time.time() - start_time, 0.000001)
            # AIResponse.duration must be mutable
            # If it's a property, set the underlying attribute
            try:
                raw_response.duration = elapsed
            except AttributeError:
                # If duration is read-only, use metadata
                raw_response.metadata["duration"] = elapsed

        # Ensure metadata has provider info
        raw_response.metadata.setdefault("provider", provider_name)
        if model_name:
            raw_response.metadata.setdefault("model", model_name)

        return raw_response

    def create_error_response(
        self,
        error: str,
        provider_name: str,
        model_name: str | None = None,
        status_code: int | None = None,
    ) -> AIResponse:
        """
        Create an error AIResponse.

        Parameters
        ----------
        error : str
            The error message.
        provider_name : str
            The provider name.
        model_name : str | None, optional
            The model used.
        status_code : int | None, optional
            HTTP status code.

        Returns
        -------
        AIResponse
            An error response.
        """
        return AIResponse(
            success=False,
            message=error,
            provider=provider_name,
            model=model_name or "",
            metadata={
                "provider": provider_name,
                "model": model_name or "",
                "status_code": status_code,
                "error": error,
            },
        )
