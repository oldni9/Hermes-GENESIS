"""
===============================================================================
Hermes Network AI Provider

Reusable implementation layer for all HTTP/network-based AI providers.

This class is NOT BaseAIProvider.

BaseAIProvider defines the abstract interface.

This class provides concrete helpers for HTTP communication.

Architecture:

    BaseAIProvider
            ↑
    NetworkAIProvider
            ↑
    OllamaProvider
    GroqProvider
    OpenRouterProvider
    MistralProvider
    CerebrasProvider

The class MUST NOT know anything about:
    - chat
    - OCR
    - embeddings
    - vision
    - speech
    - transcription
    - generation

Those belong to concrete providers.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any

import httpx

from hermes.ai.provider import BaseAIProvider
from hermes.ai.request import AIRequest
from hermes.ai.response import AIResponse
from hermes.core.exceptions import ProviderError


class NetworkAIProvider(BaseAIProvider, ABC):
    """
    Reusable HTTP AI provider base class.

    Provides:
        - Endpoint storage
        - API key storage
        - Timeout handling
        - Retry logic with exponential backoff
        - Default headers and options
        - Startup/shutdown lifecycle
        - Health checking
        - Configuration and validation
        - Generic POST/GET helpers
        - Response parsing and error conversion

    Concrete providers inherit from this class and implement
    provider-specific logic using the protected helpers.
    """

    def __init__(self) -> None:
        """
        Initialize the network AI provider.

        All configuration starts at defaults.
        The provider is not started until startup() is called.
        """

        super().__init__()

        # ------------------------------------------------------------------
        # Configuration
        # ------------------------------------------------------------------

        self._base_url: str | None = None
        self._api_key: str | None = None
        self._timeout: float = 60.0
        self._retry_count: int = 3
        self._retry_delay: float = 1.0
        self._default_headers: dict[str, str] = {}
        self._default_options: dict[str, Any] = {}

        # ------------------------------------------------------------------
        # Runtime
        # ------------------------------------------------------------------

        self._client: httpx.Client | None = None
        self._started: bool = False

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def configure(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: float | None = None,
        retry_count: int | None = None,
        retry_delay: float | None = None,
        headers: dict[str, str] | None = None,
        options: dict[str, Any] | None = None,
    ) -> None:
        """
        Configure the provider before startup.

        Parameters
        ----------
        base_url : str | None, optional
            Base URL for all requests.
        api_key : str | None, optional
            API key for authentication.
        timeout : float | None, optional
            Request timeout in seconds.
        retry_count : int | None, optional
            Number of retry attempts.
        retry_delay : float | None, optional
            Initial retry delay in seconds.
        headers : dict[str, str] | None, optional
            Default headers to send with every request.
        options : dict[str, Any] | None, optional
            Default request options.
        """

        if base_url is not None:
            self._base_url = base_url

        if api_key is not None:
            self._api_key = api_key

        if timeout is not None:
            self._timeout = timeout

        if retry_count is not None:
            self._retry_count = retry_count

        if retry_delay is not None:
            self._retry_delay = retry_delay

        if headers is not None:
            self._default_headers.update(headers)

        if options is not None:
            self._default_options.update(options)

    # ------------------------------------------------------------------

    def validate(self) -> None:
        """
        Validate configuration.

        Raises
        ------
        ValueError
            If base_url is missing.
        """

        if not self._base_url:
            raise ValueError(
                f"{self.metadata.name}: base_url is required."
            )

    # ------------------------------------------------------------------

    def merge_headers(
        self,
        override: dict[str, str] | None = None,
    ) -> dict[str, str]:
        """
        Merge default headers with override headers.

        Parameters
        ----------
        override : dict[str, str] | None, optional
            Headers to override.

        Returns
        -------
        dict[str, str]
            Merged headers.
        """

        if override is None:
            return self._default_headers.copy()

        headers = self._default_headers.copy()
        headers.update(override)

        return headers

    # ------------------------------------------------------------------

    def merge_options(
        self,
        override: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Merge default options with override options.

        Parameters
        ----------
        override : dict[str, Any] | None, optional
            Options to override.

        Returns
        -------
        dict[str, Any]
            Merged options.
        """

        if override is None:
            return self._default_options.copy()

        options = self._default_options.copy()
        options.update(override)

        return options

    # ------------------------------------------------------------------

    def prepare_request(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Prepare request payload for the provider.

        Override this in concrete providers if necessary.

        Parameters
        ----------
        payload : dict[str, Any]
            Raw payload.

        Returns
        -------
        dict[str, Any]
            Prepared payload.
        """

        return payload

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def startup(self) -> None:
        """
        Start the provider.

        Creates the HTTP client and validates configuration.

        Raises
        ------
        RuntimeError
            If validation fails.
        """

        if self._started:
            return

        self.validate()

        self._client = httpx.Client(
            base_url=self._base_url,
            timeout=self._timeout,
            headers=self._default_headers.copy(),
        )

        self._started = True

    # ------------------------------------------------------------------

    def shutdown(self) -> None:
        """
        Shut down the provider.

        Closes the HTTP client.
        """

        if not self._started:
            return

        if self._client is not None:
            self._client.close()
            self._client = None

        self._started = False

    # ------------------------------------------------------------------

    def healthy(self) -> bool:
        """
        Check whether the provider is healthy.

        Returns
        -------
        bool
            True if started and client exists, False otherwise.
        """

        return self._started and self._client is not None

    # ------------------------------------------------------------------
    # HTTP Helpers
    # ------------------------------------------------------------------

    def _headers(
        self,
        override: dict[str, str] | None = None,
    ) -> dict[str, str]:
        """
        Get merged headers for the request.

        Parameters
        ----------
        override : dict[str, str] | None, optional
            Headers to override.

        Returns
        -------
        dict[str, str]
            Merged headers.
        """

        return self.merge_headers(override)

    # ------------------------------------------------------------------

    def _prepare_payload(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Prepare payload for the request.

        Delegates to prepare_request().

        Parameters
        ----------
        payload : dict[str, Any]
            Raw payload.

        Returns
        -------
        dict[str, Any]
            Prepared payload.
        """

        return self.prepare_request(payload)

    # ------------------------------------------------------------------

    def _check_response(
        self,
        response: httpx.Response,
    ) -> None:
        """
        Check response status.

        Raises ProviderError on failure.

        Parameters
        ----------
        response : httpx.Response
            Response to check.

        Raises
        ------
        ProviderError
            If status code indicates failure.
        """

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            self._raise_error(e)

    # ------------------------------------------------------------------

    def _raise_error(
        self,
        error: httpx.HTTPStatusError,
    ) -> None:
        """
        Convert HTTP error to ProviderError.

        Parameters
        ----------
        error : httpx.HTTPStatusError
            The HTTP error to convert.

        Raises
        ------
        ProviderError
            Always raises.
        """

        raise ProviderError(
            f"{self.metadata.name}: HTTP {error.response.status_code} - {error.response.text[:200]}"
        ) from error

    # ------------------------------------------------------------------

    def _parse_response(
        self,
        response: httpx.Response,
    ) -> dict[str, Any] | str:
        """
        Parse response content.

        Tries JSON first, falls back to text.

        Parameters
        ----------
        response : httpx.Response
            Response to parse.

        Returns
        -------
        dict[str, Any] | str
            Parsed response content.
        """

        content_type = response.headers.get("content-type", "")

        if "application/json" in content_type:
            try:
                return response.json()
            except Exception:
                pass

        return response.text

    # ------------------------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        *,
        headers: dict[str, str] | None = None,
        options: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any] | str:
        """
        Generic HTTP request with retry logic.

        Parameters
        ----------
        method : str
            HTTP method (GET, POST, etc.).
        path : str
            Request path.
        headers : dict[str, str] | None, optional
            Request headers.
        options : dict[str, Any] | None, optional
            Additional request options.
        json : dict[str, Any] | None, optional
            JSON payload.
        data : dict[str, Any] | None, optional
            Form data payload.
        params : dict[str, Any] | None, optional
            Query parameters.

        Returns
        -------
        dict[str, Any] | str
            Parsed response.

        Raises
        ------
        ProviderError
            On request failure.
        RuntimeError
            If provider is not started.
        """

        if not self._started:
            raise RuntimeError(
                f"{self.metadata.name}: provider not started."
            )

        if self._client is None:
            raise RuntimeError(
                f"{self.metadata.name}: HTTP client is None."
            )

        # Merge headers and options
        request_headers = self._headers(headers)
        request_options = self._default_options.copy()

        if options:
            request_options.update(options)

        # Retry loop with exponential backoff
        last_error: Exception | None = None

        for attempt in range(self._retry_count + 1):
            try:
                response = self._client.request(
                    method=method,
                    url=path,
                    headers=request_headers,
                    params=params,
                    json=json,
                    data=data,
                    **request_options,
                )

                self._check_response(response)

                return self._parse_response(response)

            except (httpx.TimeoutException, httpx.NetworkError) as e:
                last_error = e

                if attempt >= self._retry_count:
                    raise ProviderError(
                        f"{self.metadata.name}: request failed after {self._retry_count} retries: {e}"
                    ) from e

                # Exponential backoff
                delay = self._retry_delay * (2 ** attempt)
                time.sleep(delay)

            except ProviderError:
                # Re-raise ProviderError directly
                raise

            except Exception as e:
                last_error = e
                raise ProviderError(
                    f"{self.metadata.name}: unexpected error: {e}"
                ) from e

        # Should not reach here, but keep linter happy
        raise ProviderError(
            f"{self.metadata.name}: request failed."
        ) from last_error

    # ------------------------------------------------------------------

    def _get(
        self,
        path: str,
        *,
        headers: dict[str, str] | None = None,
        options: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any] | str:
        """
        HTTP GET request.

        Parameters
        ----------
        path : str
            Request path.
        headers : dict[str, str] | None, optional
            Request headers.
        options : dict[str, Any] | None, optional
            Additional request options.
        params : dict[str, Any] | None, optional
            Query parameters.

        Returns
        -------
        dict[str, Any] | str
            Parsed response.
        """

        return self._request(
            method="GET",
            path=path,
            headers=headers,
            options=options,
            params=params,
        )

    # ------------------------------------------------------------------

    def _post(
        self,
        path: str,
        *,
        headers: dict[str, str] | None = None,
        options: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any] | str:
        """
        HTTP POST request.

        Parameters
        ----------
        path : str
            Request path.
        headers : dict[str, str] | None, optional
            Request headers.
        options : dict[str, Any] | None, optional
            Additional request options.
        json : dict[str, Any] | None, optional
            JSON payload.
        data : dict[str, Any] | None, optional
            Form data payload.
        params : dict[str, Any] | None, optional
            Query parameters.

        Returns
        -------
        dict[str, Any] | str
            Parsed response.
        """

        return self._request(
            method="POST",
            path=path,
            headers=headers,
            options=options,
            json=json,
            data=data,
            params=params,
        )

    # ------------------------------------------------------------------
    # Request/Response Serialization Helpers (to be overridden)
    # ------------------------------------------------------------------

    def _serialize_request(
        self,
        request: AIRequest,
    ) -> dict[str, Any]:
        """
        Serialize AIRequest to provider-native format.

        Override this in concrete providers.

        Parameters
        ----------
        request : AIRequest
            The request to serialize.

        Returns
        -------
        dict[str, Any]
            Provider-native request payload.
        """

        # Default: just use the request's input and prompt
        payload: dict[str, Any] = {}

        if request.prompt:
            payload["prompt"] = request.prompt

        if request.input:
            payload["input"] = request.input

        if request.options:
            payload.update(request.options)

        return payload

    # ------------------------------------------------------------------

    def _deserialize_response(
        self,
        data: dict[str, Any],
    ) -> AIResponse:
        """
        Deserialize provider-native response to AIResponse.

        Override this in concrete providers.

        Parameters
        ----------
        data : dict[str, Any]
            Provider-native response data.

        Returns
        -------
        AIResponse
            Standardized AIResponse.
        """

        return AIResponse(
            success=True,
            result=data,
        )

    # ------------------------------------------------------------------

    def _build_error_response(
        self,
        message: str,
        status: int = 500,
    ) -> AIResponse:
        """
        Build an error AIResponse.

        Parameters
        ----------
        message : str
            Error message.
        status : int, default=500
            HTTP status code.

        Returns
        -------
        AIResponse
            Error response.
        """

        return AIResponse(
            success=False,
            message=message,
            metadata={"status": status},
        )

    # ------------------------------------------------------------------
    # Abstract execute (must be implemented by concrete providers)
    # ------------------------------------------------------------------

    @abstractmethod
    def execute(
        self,
        request: AIRequest,
        context: Any = None,
    ) -> AIResponse:
        """
        Execute an AI request.

        Concrete providers must implement this.

        Parameters
        ----------
        request : AIRequest
            The request to execute.
        context : Any, optional
            Execution context.

        Returns
        -------
        AIResponse
            The response.
        """