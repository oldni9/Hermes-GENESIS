"""
===============================================================================
Hermes OpenRouter Provider

Concrete provider for OpenRouter API.

Inherits from NetworkAIProvider.

Implements:
    - /chat/completions (chat and generate)
    - /models (list models)

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from typing import Any

from hermes.ai.metadata import AIMetadata
from hermes.ai.providers.base_provider import NetworkAIProvider
from hermes.ai.request import AIRequest
from hermes.ai.response import AIResponse
from hermes.core.exceptions import ProviderError


class OpenRouterProvider(NetworkAIProvider):
    """
    OpenRouter AI provider.

    Communicates with the OpenRouter API via HTTP.

    Supports:
        - Chat completion (/chat/completions)
        - Model listing (/models)
    """

    # ------------------------------------------------------------------
    # Private Endpoint Constants
    # ------------------------------------------------------------------

    _CHAT = "/chat/completions"
    _MODELS = "/models"

    # ------------------------------------------------------------------
    # Supported Options (for _build_common_options)
    # ------------------------------------------------------------------

    _SUPPORTED_OPTIONS = {
        "temperature",
        "top_p",
        "top_k",
        "frequency_penalty",
        "presence_penalty",
        "max_tokens",
        "stop",
        "seed",
        "stream",
        "response_format",
        "tools",
        "tool_choice",
        "logit_bias",
    }

    # ------------------------------------------------------------------

    def __init__(self) -> None:
        """
        Initialize the OpenRouter provider.

        Sets up metadata and default configuration.
        """

        super().__init__()

        self._metadata = AIMetadata(
            name="openrouter",
            provider="openrouter",
            version="1.0",
            capabilities=[
                "chat",
                "generate",
                "list_models",
            ],
        )

        self._default_model: str | None = None
        self._auto_detected: bool = False

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    @property
    def metadata(self) -> AIMetadata:
        """
        Return provider metadata.

        Returns
        -------
        AIMetadata
            Provider metadata.
        """

        return self._metadata

    # ------------------------------------------------------------------

    @property
    def default_model(self) -> str | None:
        """
        Return the default model for this provider.

        Returns
        -------
        str | None
            Default model name, or None if not configured.
        """

        return self._default_model

    # ------------------------------------------------------------------
    # Core Configuration
    # ------------------------------------------------------------------

    def configure(
        self,
        base_url: str = "https://openrouter.ai/api/v1",
        api_key: str | None = None,
        timeout: float = 60.0,
        retry_count: int = 3,
        retry_delay: float = 1.0,
        default_model: str | None = None,
        **kwargs,
    ) -> None:
        """
        Configure the OpenRouter provider.

        Parameters
        ----------
        base_url : str, default="https://openrouter.ai/api/v1"
            OpenRouter API base URL.
        api_key : str | None, optional
            API key for authentication (required).
        timeout : float, default=60.0
            Request timeout in seconds.
        retry_count : int, default=3
            Number of retry attempts.
        retry_delay : float, default=1.0
            Initial retry delay in seconds.
        default_model : str | None, optional
            Default model to use if not specified in request.
            If None, will auto-detect on startup.
        **kwargs
            Additional configuration options (e.g., additional headers).
        """

        # Ensure api_key is provided
        if api_key is None:
            raise ValueError(f"{self.metadata.name}: api_key is required.")

        # Set Authorization header
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {api_key}"

        # Add OpenRouter recommended headers
        if "HTTP-Referer" not in headers:
            headers["HTTP-Referer"] = "https://hermes.ai"
        if "X-Title" not in headers:
            headers["X-Title"] = "Hermes Genesis"

        super().configure(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
            retry_count=retry_count,
            retry_delay=retry_delay,
            headers=headers,
            **kwargs,
        )

        self._default_model = default_model

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def startup(self) -> None:
        """
        Start the provider.

        Validates that the OpenRouter API is reachable.

        If no default model is configured, auto-detects the first available model,
        preferring free models and then a sensible fallback.

        Raises
        ------
        ProviderError
            If the API is not reachable or no models are available.
        """

        super().startup()

        if not self.healthy():
            raise ProviderError(
                f"{self.metadata.name}: health check failed. "
                "Unable to reach OpenRouter API. Check your API key and network."
            )

        # Auto-detect default model if not configured
        if self._default_model is None:
            models = self.list_models()

            if not models:
                raise ProviderError(
                    f"{self.metadata.name}: no models available. "
                    "Check your OpenRouter account."
                )

            # 1. Try to find a free model
            for model in models:
                pricing = model.get("pricing", {})
                prompt_price = pricing.get("prompt", 0)
                completion_price = pricing.get("completion", 0)
                if prompt_price == 0 and completion_price == 0:
                    self._default_model = model.get("id")
                    self._auto_detected = True
                    break

            # 2. Fallback to a well-known free/open model
            if self._default_model is None:
                fallback_candidates = [
                    "openai/gpt-4.1-mini",
                    "openai/gpt-3.5-turbo",
                    "meta-llama/llama-3.2-3b-instruct",
                    "mistralai/mistral-7b-instruct",
                ]
                for candidate in fallback_candidates:
                    for model in models:
                        if model.get("id") == candidate:
                            self._default_model = candidate
                            self._auto_detected = True
                            break
                    if self._default_model is not None:
                        break

            # 3. Last resort: first available model
            if self._default_model is None:
                self._default_model = models[0].get("id")
                self._auto_detected = True

            if not self._default_model:
                raise ProviderError(
                    f"{self.metadata.name}: could not determine model id from server response."
                )

    # ------------------------------------------------------------------

    def healthy(self) -> bool:
        """
        Check if the OpenRouter API is healthy.

        Uses GET /models to verify connectivity and authentication.

        Returns
        -------
        bool
            True if API responds successfully, False otherwise.
        """

        if not self._started or self._client is None:
            return False

        try:
            self._get(self._MODELS)
            return True
        except ProviderError:
            return False

    # ------------------------------------------------------------------
    # Core AI Execution
    # ------------------------------------------------------------------

    def execute(
        self,
        request: AIRequest,
        context: Any = None,
    ) -> AIResponse:
        """
        Execute an AI request against OpenRouter.

        Supports two modes:
            - Chat: uses /chat/completions with messages
            - Generate: uses /chat/completions with a single user message

        The mode is determined by:
            - request.task == "generate" (explicit generate)
            - otherwise uses chat.

        Parameters
        ----------
        request : AIRequest
            The request to execute.
        context : Any, optional
            Execution context (unused).

        Returns
        -------
        AIResponse
            Standardized AIResponse.

        Raises
        ------
        ProviderError
            On request failure or if no model is available.
        """

        if request.task == "generate":
            return self._generate(request)

        # Default to chat
        return self._chat(request)

    # ------------------------------------------------------------------

    def batch_execute(
        self,
        requests: list[AIRequest],
        context: Any = None,
    ) -> list[AIResponse]:
        """
        Execute multiple requests sequentially.

        Parameters
        ----------
        requests : list[AIRequest]
            List of requests to execute.
        context : Any, optional
            Execution context.

        Returns
        -------
        list[AIResponse]
            List of responses in the same order.
        """

        responses: list[AIResponse] = []

        for req in requests:
            responses.append(self.execute(req, context))

        return responses

    # ------------------------------------------------------------------
    # Model Management
    # ------------------------------------------------------------------

    def list_models(self) -> list[dict[str, Any]]:
        """
        List available models.

        Returns
        -------
        list[dict[str, Any]]
            List of model information dictionaries.

        Raises
        ------
        ProviderError
            On request failure.
        """

        response = self._get(self._MODELS)

        # OpenRouter returns a list of models directly
        if isinstance(response, list):
            return response

        if isinstance(response, dict):
            # Some versions might wrap in "data" field
            if "data" in response:
                return response["data"]

        raise ProviderError(
            f"{self.metadata.name}: unexpected response format from {self._MODELS}"
        )

    # ------------------------------------------------------------------

    def model_exists(self, model: str) -> bool:
        """
        Check if a model exists on OpenRouter.

        Performs exact match first, then falls back to
        case-insensitive comparison.

        Parameters
        ----------
        model : str
            Model name.

        Returns
        -------
        bool
            True if model exists, False otherwise.
        """

        try:
            models = self.list_models()
            model_ids = [m.get("id", "") for m in models]

            # Exact match
            if model in model_ids:
                return True

            # Case-insensitive match
            model_lower = model.lower()
            for m_id in model_ids:
                if m_id.lower() == model_lower:
                    return True

            return False

        except ProviderError:
            return False

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    def _generate(self, request: AIRequest) -> AIResponse:
        """
        Execute a generate request (single user message).

        Parameters
        ----------
        request : AIRequest
            The request.

        Returns
        -------
        AIResponse
            Response object.
        """

        payload = self._build_generate_payload(request)

        try:
            result = self._post(self._CHAT, json=payload)
        except ProviderError as e:
            return self._build_error_response(str(e), status=500)

        return self._parse_completion_response(result)

    # ------------------------------------------------------------------

    def _chat(self, request: AIRequest) -> AIResponse:
        """
        Execute a chat request.

        Parameters
        ----------
        request : AIRequest
            The request.

        Returns
        -------
        AIResponse
            Response object.
        """

        payload = self._build_chat_payload(request)

        try:
            result = self._post(self._CHAT, json=payload)
        except ProviderError as e:
            return self._build_error_response(str(e), status=500)

        return self._parse_completion_response(result)

    # ------------------------------------------------------------------
    # Payload Builders
    # ------------------------------------------------------------------

    def _build_common_options(self, options: dict[str, Any]) -> dict[str, Any]:
        """
        Extract common OpenRouter options from request options.

        Uses a supported options set for maintainability.

        Parameters
        ----------
        options : dict[str, Any]
            Request options.

        Returns
        -------
        dict[str, Any]
            Common options for OpenRouter API.
        """

        result: dict[str, Any] = {}

        for key in self._SUPPORTED_OPTIONS:
            if key in options:
                result[key] = options[key]

        return result

    # ------------------------------------------------------------------

    def _get_model(self, request: AIRequest) -> str:
        """
        Get the model to use for a request.

        Prioritizes request.model, falls back to default_model.

        Parameters
        ----------
        request : AIRequest
            The request.

        Returns
        -------
        str
            Model name.

        Raises
        ------
        ProviderError
            If no model is available.
        """

        if request.model:
            return request.model

        if self._default_model is None:
            raise ProviderError(
                f"{self.metadata.name}: no default model configured. "
                "Configure default_model or pass request.model."
            )

        return self._default_model

    # ------------------------------------------------------------------

    def _build_generate_payload(self, request: AIRequest) -> dict[str, Any]:
        """
        Build payload for /chat/completions for generate.

        Parameters
        ----------
        request : AIRequest
            The request.

        Returns
        -------
        dict[str, Any]
            Payload for OpenRouter chat completions API.

        Raises
        ------
        ProviderError
            If prompt or input is missing, or no model available.
        """

        payload: dict[str, Any] = {
            "model": self._get_model(request),
        }

        # Build messages with a single user message
        if request.prompt:
            content = request.prompt
        elif request.input:
            content = str(request.input)
        else:
            raise ProviderError(
                f"{self.metadata.name}: request must have either prompt or input for generation."
            )

        messages = [{"role": "user", "content": content}]
        payload["messages"] = messages

        # Options
        common = self._build_common_options(request.options)
        payload.update(common)

        return payload

    # ------------------------------------------------------------------

    def _build_chat_payload(self, request: AIRequest) -> dict[str, Any]:
        """
        Build payload for /chat/completions for chat.

        Parameters
        ----------
        request : AIRequest
            The request.

        Returns
        -------
        dict[str, Any]
            Payload for OpenRouter chat completions API.

        Raises
        ------
        ProviderError
            If messages or prompt/input is missing, or no model available.
        """

        payload: dict[str, Any] = {
            "model": self._get_model(request),
        }

        messages = request.options.get("messages")

        if not messages:
            if request.prompt:
                messages = [{"role": "user", "content": request.prompt}]
            elif request.input:
                messages = [{"role": "user", "content": str(request.input)}]
            else:
                raise ProviderError(
                    f"{self.metadata.name}: chat request must have messages or a prompt/input."
                )

        payload["messages"] = messages

        # Options
        common = self._build_common_options(request.options)
        payload.update(common)

        return payload

    # ------------------------------------------------------------------
    # Response Parsers
    # ------------------------------------------------------------------

    def _parse_completion_response(self, raw: dict[str, Any]) -> AIResponse:
        """
        Parse /chat/completions response for both chat and generate.

        Parameters
        ----------
        raw : dict[str, Any]
            Raw response from OpenRouter.

        Returns
        -------
        AIResponse
            Standardized response.
        """

        if "error" in raw:
            return AIResponse(
                success=False,
                message=raw["error"].get("message", str(raw["error"])),
                metadata=raw,
            )

        choices = raw.get("choices", [])
        if not choices:
            return AIResponse(
                success=False,
                message="No choices in response",
                metadata=raw,
            )

        choice = choices[0]
        message = choice.get("message", {})
        content = message.get("content", "")

        return AIResponse(
            success=True,
            result=content,
            metadata={
                "provider": "openrouter",
                "model": raw.get("model"),
                "id": raw.get("id"),
                "created": raw.get("created"),
                "object": raw.get("object"),
                "finish_reason": choice.get("finish_reason"),
                "usage": raw.get("usage"),
                # Do not include full raw response; it's huge and couples the provider.
            },
        )

    # ------------------------------------------------------------------
    # Error Handling
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
            metadata={
                "provider": "openrouter",
                "status": status,
            },
        )
