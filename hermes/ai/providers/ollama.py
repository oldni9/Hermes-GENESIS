"""
===============================================================================
Hermes Ollama Provider

Concrete provider for Ollama local inference server.

Inherits from NetworkAIProvider.

Implements:
    - /api/generate (text generation)
    - /api/chat (chat completion)
    - /api/tags (list models)
    - /api/pull (pull model)
    - /api/delete (delete model)

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


class OllamaProvider(NetworkAIProvider):
    """
    Ollama AI provider.

    Communicates with a local Ollama server via HTTP.

    Supports:
        - Text generation (/api/generate)
        - Chat completion (/api/chat)
        - Model listing (/api/tags)
        - Model pulling (/api/pull)
        - Model deletion (/api/delete)
    """

    # ------------------------------------------------------------------
    # Private Endpoint Constants
    # ------------------------------------------------------------------

    _GENERATE = "/api/generate"
    _CHAT = "/api/chat"
    _TAGS = "/api/tags"
    _PULL = "/api/pull"
    _DELETE = "/api/delete"

    # ------------------------------------------------------------------
    # Supported Options (for _build_common_options)
    # ------------------------------------------------------------------

    _SUPPORTED_OPTIONS = {
        "temperature",
        "top_p",
        "top_k",
        "seed",
        "num_predict",
        "num_ctx",
        "repeat_penalty",
        "repeat_last_n",
        "mirostat",
        "mirostat_eta",
        "mirostat_tau",
    }

    # ------------------------------------------------------------------

    def __init__(self) -> None:
        """
        Initialize the Ollama provider.

        Sets up metadata and default configuration.
        """

        super().__init__()

        self._metadata = AIMetadata(
            name="ollama",
            provider="ollama",
            version="1.0",
            capabilities=[
                "generate",
                "chat",
                "list_models",
                "pull_model",
                "delete_model",
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
        base_url: str = "http://localhost:11434",
        api_key: str | None = None,
        timeout: float = 120.0,
        retry_count: int = 3,
        retry_delay: float = 1.0,
        default_model: str | None = None,
        **kwargs,
    ) -> None:
        """
        Configure the Ollama provider.

        Parameters
        ----------
        base_url : str, default="http://localhost:11434"
            Ollama server base URL.
        api_key : str | None, optional
            Not used for Ollama, kept for API consistency.
        timeout : float, default=120.0
            Request timeout in seconds.
        retry_count : int, default=3
            Number of retry attempts.
        retry_delay : float, default=1.0
            Initial retry delay in seconds.
        default_model : str | None, optional
            Default model to use if not specified in request.
            If None, will auto-detect on startup.
        **kwargs
            Additional configuration options.
        """

        super().configure(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
            retry_count=retry_count,
            retry_delay=retry_delay,
            **kwargs,
        )

        self._default_model = default_model

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def startup(self) -> None:
        """
        Start the provider.

        Validates that the Ollama server is reachable.

        If no default model is configured, auto-detects the first available model.

        Raises
        ------
        ProviderError
            If the server is not reachable or no models are available.
        """

        super().startup()

        if not self.healthy():
            raise ProviderError(
                f"{self.metadata.name}: health check failed. "
                "Is the Ollama server running?"
            )

        # Auto-detect default model if not configured
        if self._default_model is None:
            models = self.list_models()

            if not models:
                raise ProviderError(
                    f"{self.metadata.name}: no models available. "
                    "Pull a model first (e.g., ollama pull llama3.2)."
                )

            # Use the first available model
            first_model = models[0].get("name")

            if not first_model:
                raise ProviderError(
                    f"{self.metadata.name}: could not determine model name from server response."
                )

            self._default_model = first_model
            self._auto_detected = True

    # ------------------------------------------------------------------

    def healthy(self) -> bool:
        """
        Check if the Ollama server is healthy.

        Uses GET /api/tags to verify connectivity.

        Returns
        -------
        bool
            True if server responds successfully, False otherwise.
        """

        if not self._started or self._client is None:
            return False

        try:
            self._get(self._TAGS)
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
        Execute an AI request against Ollama.

        Supports two modes:
            - Generate: uses /api/generate
            - Chat: uses /api/chat

        The mode is determined by:
            - request.task == "chat" (explicit)
            - presence of "messages" in request.options
            - otherwise uses generate.

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

        if request.task == "chat" or "messages" in request.options:
            return self._chat(request)

        return self._generate(request)

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

        response = self._get(self._TAGS)

        if not isinstance(response, dict):
            raise ProviderError(
                f"{self.metadata.name}: unexpected response format from {self._TAGS}"
            )

        return response.get("models", [])

    # ------------------------------------------------------------------

    def pull_model(
        self,
        model: str,
        stream: bool = False,
    ) -> dict[str, Any] | str:
        """
        Pull a model from the registry.

        Parameters
        ----------
        model : str
            Model name (e.g., "llama3.2").
        stream : bool, default=False
            Whether to stream the pull progress.

        Returns
        -------
        dict[str, Any] | str
            Pull response (status or stream content).

        Raises
        ------
        ProviderError
            On request failure.
        """

        payload = {"name": model, "stream": stream}

        if stream:
            raise NotImplementedError(
                f"{self.metadata.name}: streaming pull not implemented"
            )

        return self._post(self._PULL, json=payload)

    # ------------------------------------------------------------------

    def delete_model(self, model: str) -> dict[str, Any]:
        """
        Delete a model.

        Parameters
        ----------
        model : str
            Model name.

        Returns
        -------
        dict[str, Any]
            Deletion response.

        Raises
        ------
        ProviderError
            On request failure.
        """

        payload = {"name": model}
        return self._post(self._DELETE, json=payload)

    # ------------------------------------------------------------------

    def model_exists(self, model: str) -> bool:
        """
        Check if a model exists on the server.

        Performs exact match first, then falls back to
        tag-stripped comparison.

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
            model_names = [m.get("name", "") for m in models]

            # Exact match
            if model in model_names:
                return True

            # Normalized match (strip tags)
            normalized_target = model.split(":")[0]

            for name in model_names:
                normalized_name = name.split(":")[0]

                if normalized_name == normalized_target:
                    return True

            return False

        except ProviderError:
            return False

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    def _generate(self, request: AIRequest) -> AIResponse:
        """
        Execute a generate request.

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
            result = self._post(self._GENERATE, json=payload)
        except ProviderError as e:
            return self._build_error_response(str(e), status=500)

        return self._parse_generate_response(result)

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

        return self._parse_chat_response(result)

    # ------------------------------------------------------------------
    # Payload Builders
    # ------------------------------------------------------------------

    def _build_common_options(self, options: dict[str, Any]) -> dict[str, Any]:
        """
        Extract common Ollama options from request options.

        Uses a supported options set for maintainability.

        Parameters
        ----------
        options : dict[str, Any]
            Request options.

        Returns
        -------
        dict[str, Any]
            Common options for Ollama API.
        """

        result: dict[str, Any] = {}

        for key in self._SUPPORTED_OPTIONS:
            if key in options:
                result[key] = options[key]

        # Always include stream, defaulting to False
        if "stream" not in result:
            result["stream"] = False

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
        Build payload for /api/generate.

        Parameters
        ----------
        request : AIRequest
            The request.

        Returns
        -------
        dict[str, Any]
            Payload for Ollama generate API.

        Raises
        ------
        ProviderError
            If prompt or input is missing, or no model available.
        """

        payload: dict[str, Any] = {
            "model": self._get_model(request),
            "stream": False,
        }

        if request.prompt:
            payload["prompt"] = request.prompt
        elif request.input:
            payload["prompt"] = str(request.input)
        else:
            raise ProviderError(
                f"{self.metadata.name}: request must have either prompt or input for generation."
            )

        # Options
        common = self._build_common_options(request.options)
        payload.update(common)

        # Additional generate-specific options
        for key in ["system", "template", "context", "format", "keep_alive"]:
            if key in request.options:
                payload[key] = request.options[key]

        return payload

    # ------------------------------------------------------------------

    def _build_chat_payload(self, request: AIRequest) -> dict[str, Any]:
        """
        Build payload for /api/chat.

        Parameters
        ----------
        request : AIRequest
            The request.

        Returns
        -------
        dict[str, Any]
            Payload for Ollama chat API.

        Raises
        ------
        ProviderError
            If messages or prompt/input is missing, or no model available.
        """

        payload: dict[str, Any] = {
            "model": self._get_model(request),
            "stream": False,
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

        # Additional chat-specific options
        if "system" in request.options:
            payload["system"] = request.options["system"]
        if "keep_alive" in request.options:
            payload["keep_alive"] = request.options["keep_alive"]

        return payload

    # ------------------------------------------------------------------
    # Response Parsers
    # ------------------------------------------------------------------

    def _parse_generate_response(self, raw: dict[str, Any]) -> AIResponse:
        """
        Parse /api/generate response.

        Parameters
        ----------
        raw : dict[str, Any]
            Raw response from Ollama.

        Returns
        -------
        AIResponse
            Standardized response.
        """

        if "error" in raw:
            return AIResponse(
                success=False,
                message=raw["error"],
                metadata=raw,
            )

        return AIResponse(
            success=True,
            result=raw.get("response", ""),
            metadata={
                "provider": "ollama",
                "model": raw.get("model"),
                "created_at": raw.get("created_at"),
                "done": raw.get("done", True),
                "context": raw.get("context"),
                "total_duration": raw.get("total_duration"),
                "load_duration": raw.get("load_duration"),
                "prompt_eval_count": raw.get("prompt_eval_count"),
                "eval_count": raw.get("eval_count"),
                "eval_duration": raw.get("eval_duration"),
            },
        )

    # ------------------------------------------------------------------

    def _parse_chat_response(self, raw: dict[str, Any]) -> AIResponse:
        """
        Parse /api/chat response.

        Parameters
        ----------
        raw : dict[str, Any]
            Raw response from Ollama.

        Returns
        -------
        AIResponse
            Standardized response.
        """

        if "error" in raw:
            return AIResponse(
                success=False,
                message=raw["error"],
                metadata=raw,
            )

        message = raw.get("message", {})
        content = message.get("content", "")

        return AIResponse(
            success=True,
            result=content,
            metadata={
                "provider": "ollama",
                "model": raw.get("model"),
                "created_at": raw.get("created_at"),
                "done": raw.get("done", True),
                "message": message,
                "total_duration": raw.get("total_duration"),
                "load_duration": raw.get("load_duration"),
                "prompt_eval_count": raw.get("prompt_eval_count"),
                "eval_count": raw.get("eval_count"),
                "eval_duration": raw.get("eval_duration"),
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
                "provider": "ollama",
                "status": status,
            },
        )
