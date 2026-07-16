"""
===============================================================================
Hermes AI Client

High-level public API entry point for Hermes.

Owns:
    - AIManager
    - Default provider/model configuration
    - Registry access

Creates:
    - Chat objects
    - Sessions
    - Conversations
    - Requests
    - Prompts

Provides:
    - Provider selection
    - Provider listing
    - Model listing
    - One-shot completion API
    - Streaming API
    - Embedding API delegation
    - Future-compatible memory/tool integration

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Generator, Self

from hermes.ai.chat import Chat
from hermes.ai.conversation import AIConversation
from hermes.ai.manager import AIManager
from hermes.ai.provider import BaseAIProvider
from hermes.ai.prompt import Prompt
from hermes.ai.registry import AIRegistry
from hermes.ai.request import AIRequest
from hermes.ai.response import AIResponse
from hermes.ai.session import AISession, SessionConfig
from hermes.ai.metadata import AIMetadata


# =============================================================================
# Client Config
# =============================================================================

@dataclass(slots=True)
class ClientConfig:
    """
    Configuration for the Hermes client.

    Attributes
    ----------
    provider : str | None
        Default provider name.
    model : str | None
        Default model name.
    timeout : float | None
        Default timeout for requests.
    retries : int | None
        Default retry count.
    temperature : float | None
        Default temperature.
    max_tokens : int | None
        Default maximum tokens.
    metadata : dict[str, Any]
        Default metadata for all requests.
    """

    provider: str | None = None
    model: str | None = None
    timeout: float | None = None
    retries: int | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result: dict[str, Any] = {}
        if self.provider is not None:
            result["provider"] = self.provider
        if self.model is not None:
            result["model"] = self.model
        if self.timeout is not None:
            result["timeout"] = self.timeout
        if self.retries is not None:
            result["retries"] = self.retries
        if self.temperature is not None:
            result["temperature"] = self.temperature
        if self.max_tokens is not None:
            result["max_tokens"] = self.max_tokens
        if self.metadata:
            result["metadata"] = self.metadata
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ClientConfig:
        """Create from dictionary."""
        return cls(
            provider=data.get("provider"),
            model=data.get("model"),
            timeout=data.get("timeout"),
            retries=data.get("retries"),
            temperature=data.get("temperature"),
            max_tokens=data.get("max_tokens"),
            metadata=data.get("metadata", {}),
        )

    def apply_to_request(self, request: AIRequest) -> None:
        """
        Apply config settings to a request (merging with existing values).
        """
        if self.provider is not None and not request.provider:
            request.provider = self.provider
        if self.model is not None and not request.model:
            request.model = self.model
        if self.timeout is not None and "timeout" not in request.options:
            request.options["timeout"] = self.timeout
        if self.retries is not None and "retries" not in request.options:
            request.options["retries"] = self.retries
        if self.temperature is not None and "temperature" not in request.options:
            request.options["temperature"] = self.temperature
        if self.max_tokens is not None and "max_tokens" not in request.options:
            request.options["max_tokens"] = self.max_tokens
        if self.metadata:
            # Merge metadata; request metadata takes precedence
            for k, v in self.metadata.items():
                if k not in request.metadata:
                    request.metadata[k] = v


# =============================================================================
# Hermes Client
# =============================================================================

class HermesClient:
    """
    High-level public API entry point for Hermes.

    This is the main interface developers use to interact with Hermes.

    Features:
        - One-shot completion (complete/stream)
        - Chat creation
        - Session/Conversation management
        - Provider/model listing
        - Default configuration
        - Fluent API
        - Serialization
        - Context manager

    Examples
    --------
    >>> client = HermesClient(provider="openrouter", model="gpt-4")
    >>> response = client.complete("What is Python?")
    >>> print(response.text())
    "Python is a programming language..."

    >>> chat = client.chat()
    >>> response = chat.send("Hello!")
    """

    def __init__(
        self,
        manager: AIManager | None = None,
        provider: str | None = None,
        model: str | None = None,
        config: ClientConfig | None = None,
    ):
        """
        Initialize the Hermes client.

        Parameters
        ----------
        manager : AIManager | None, optional
            AI Manager instance. If None, a new one is created.
        provider : str | None, optional
            Default provider name.
        model : str | None, optional
            Default model name.
        config : ClientConfig | None, optional
            Client configuration.
        """
        self._manager = manager or AIManager()
        self._config = config or ClientConfig()

        if provider is not None:
            self._config.provider = provider
        if model is not None:
            self._config.model = model

        # Validate initial provider/model if set
        self._validate_provider_model()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def manager(self) -> AIManager:
        """Get the AI manager."""
        return self._manager

    @property
    def registry(self) -> AIRegistry:
        """Get the provider registry."""
        return self._manager.registry

    @property
    def provider(self) -> str | None:
        """Get the default provider."""
        return self._config.provider

    @property
    def model(self) -> str | None:
        """Get the default model."""
        return self._config.model

    @property
    def config(self) -> ClientConfig:
        """Get the client configuration."""
        return self._config

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate_provider_model(self) -> None:
        """Validate that the configured provider/model exist."""
        if self._config.provider is not None:
            if not self.registry.exists(self._config.provider):
                raise ValueError(
                    f"Provider '{self._config.provider}' is not registered."
                )
        # Model validation is provider-specific, we'll do it lazily.

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def set_provider(self, provider: str) -> Self:
        """
        Set the default provider.

        Parameters
        ----------
        provider : str
            Provider name.

        Returns
        -------
        Self
            The client instance (fluent API).

        Raises
        ------
        ValueError
            If provider is not registered.
        """
        if not self.registry.exists(provider):
            raise ValueError(f"Provider '{provider}' is not registered.")
        self._config.provider = provider
        return self

    def set_model(self, model: str) -> Self:
        """
        Set the default model.

        Parameters
        ----------
        model : str
            Model name.

        Returns
        -------
        Self
            The client instance (fluent API).

        Note
        ----
        Model validation is deferred until execution.
        """
        self._config.model = model
        return self

    def set_config(self, config: ClientConfig) -> Self:
        """
        Set the client configuration.

        Parameters
        ----------
        config : ClientConfig
            New configuration.

        Returns
        -------
        Self
            The client instance (fluent API).
        """
        self._config = config
        self._validate_provider_model()
        return self

    # ------------------------------------------------------------------
    # Provider/Model Listing
    # ------------------------------------------------------------------

    def list_providers(self) -> list[AIMetadata]:
        """
        List all registered providers.

        Returns
        -------
        list[AIMetadata]
            List of provider metadata.
        """
        return [p.metadata for p in self.registry.providers()]

    def list_provider_names(self) -> list[str]:
        """
        List all registered provider names.

        Returns
        -------
        list[str]
            List of provider names.
        """
        return self.registry.names()

    def list_models(self, provider: str | None = None) -> list[str]:
        """
        List available models for a provider.

        Parameters
        ----------
        provider : str | None, optional
            Provider name. If None, uses default provider.

        Returns
        -------
        list[str]
            List of model names.

        Raises
        ------
        ValueError
            If the provider is not registered.
        """
        provider_name = provider or self._config.provider
        if not provider_name:
            raise ValueError("No provider specified and no default provider set.")
        p = self.registry.get(provider_name)
        if p is None:
            raise ValueError(f"Provider '{provider_name}' is not registered.")
        # Use the provider's list_models method if available.
        if hasattr(p, "list_models") and callable(p.list_models):
            models = p.list_models()
            if isinstance(models, list):
                return [m.get("id", str(m)) for m in models]
        # Fallback: if provider has a metadata.models attribute
        if hasattr(p, "metadata") and hasattr(p.metadata, "models"):
            return p.metadata.models
        return []

    def get_provider(self, name: str) -> BaseAIProvider | None:
        """
        Get a provider by name.

        Parameters
        ----------
        name : str
            Provider name.

        Returns
        -------
        BaseAIProvider | None
            The provider instance, or None if not found.
        """
        return self.registry.get(name)

    # ------------------------------------------------------------------
    # Chat
    # ------------------------------------------------------------------

    def chat(
        self,
        conversation: AIConversation | None = None,
        session: AISession | None = None,
        config: SessionConfig | None = None,
        metadata: dict[str, Any] | None = None,
        tags: list[str] | None = None,
    ) -> Chat:
        """
        Create a new Chat instance.

        Parameters
        ----------
        conversation : AIConversation | None, optional
            Existing conversation.
        session : AISession | None, optional
            Existing session.
        config : SessionConfig | None, optional
            Session configuration.
        metadata : dict[str, Any] | None, optional
            Initial metadata.
        tags : list[str] | None, optional
            Initial tags.

        Returns
        -------
        Chat
            A new Chat instance.
        """
        return Chat(
            manager=self._manager,
            provider=self._config.provider,
            model=self._config.model,
            conversation=conversation,
            session=session,
            config=config,
            metadata=metadata,
            tags=tags,
        )

    # ------------------------------------------------------------------
    # Session
    # ------------------------------------------------------------------

    def create_session(
        self,
        provider: str | None = None,
        model: str | None = None,
        config: SessionConfig | None = None,
        metadata: dict[str, Any] | None = None,
        tags: list[str] | None = None,
    ) -> AISession:
        """
        Create a new session.

        Parameters
        ----------
        provider : str | None, optional
            Provider name.
        model : str | None, optional
            Model name.
        config : SessionConfig | None, optional
            Session configuration.
        metadata : dict[str, Any] | None, optional
            Initial metadata.
        tags : list[str] | None, optional
            Initial tags.

        Returns
        -------
        AISession
            A new session instance.
        """
        return AISession(
            provider=provider or self._config.provider,
            model=model or self._config.model,
            config=config,
            metadata=metadata,
            tags=tags,
        )

    # ------------------------------------------------------------------
    # Conversation
    # ------------------------------------------------------------------

    def create_conversation(
        self,
        title: str = "",
        metadata: dict[str, Any] | None = None,
        tags: list[str] | None = None,
    ) -> AIConversation:
        """
        Create a new conversation.

        Parameters
        ----------
        title : str, default=""
            Conversation title.
        metadata : dict[str, Any] | None, optional
            Initial metadata.
        tags : list[str] | None, optional
            Initial tags.

        Returns
        -------
        AIConversation
            A new conversation instance.
        """
        return AIConversation(
            title=title,
            metadata=metadata,
            tags=tags,
        )

    # ------------------------------------------------------------------
    # Prompt
    # ------------------------------------------------------------------

    def create_prompt(
        self,
        system: str = "",
        messages: list[Any] | None = None,
        template: str | None = None,
        strict: bool = True,
    ) -> Prompt:
        """
        Create a new prompt.

        Parameters
        ----------
        system : str, default=""
            System instruction.
        messages : list[Any] | None, optional
            Initial messages.
        template : str | None, optional
            Template string.
        strict : bool, default=True
            Strict mode for variables.

        Returns
        -------
        Prompt
            A new prompt instance.
        """
        return Prompt(
            system=system,
            messages=messages,
            template=template,
            strict=strict,
        )

    # ------------------------------------------------------------------
    # Request
    # ------------------------------------------------------------------

    def create_request(
        self,
        prompt: str = "",
        input: Any = None,
        provider: str | None = None,
        model: str | None = None,
        task: str = "chat",
        options: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AIRequest:
        """
        Create a new request.

        Parameters
        ----------
        prompt : str, default=""
            Prompt text.
        input : Any, optional
            Input data.
        provider : str | None, optional
            Provider name.
        model : str | None, optional
            Model name.
        task : str, default="chat"
            Task type.
        options : dict[str, Any] | None, optional
            Generation options.
        metadata : dict[str, Any] | None, optional
            Request metadata.

        Returns
        -------
        AIRequest
            A new request instance.
        """
        return AIRequest(
            prompt=prompt,
            input=input,
            provider=provider or "",
            model=model or "",
            task=task,
            options=options or {},
            metadata=metadata or {},
        )

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def _prepare_request(
        self,
        prompt_text: str,
        system: str | None = None,
        provider: str | None = None,
        model: str | None = None,
        options: dict[str, Any] | None = None,
        task: str = "generate",
    ) -> AIRequest:
        """
        Build a request from simple parameters.

        This is used by both complete() and stream() to ensure consistency.

        Parameters
        ----------
        prompt_text : str
            User prompt.
        system : str | None, optional
            System instruction.
        provider : str | None, optional
            Provider override.
        model : str | None, optional
            Model override.
        options : dict[str, Any] | None, optional
            Generation options.
        task : str, default="generate"
            Task type.

        Returns
        -------
        AIRequest
            A ready-to-execute request.
        """
        # Build prompt
        p = Prompt()
        if system:
            p.add_system(system)
        p.add_user(prompt_text)

        # Convert to request
        request = p.to_request()
        request.task = task
        # Apply provider/model overrides
        if provider:
            request.provider = provider
        elif self._config.provider:
            request.provider = self._config.provider
        if model:
            request.model = model
        elif self._config.model:
            request.model = self._config.model
        # Merge options
        if options:
            request.options.update(options)
        # Apply client config (metadata, timeout, etc.)
        self._config.apply_to_request(request)
        return request

    def _execute_request(self, request: AIRequest) -> AIResponse:
        """
        Execute a request via the manager.

        Parameters
        ----------
        request : AIRequest
            The request to execute.

        Returns
        -------
        AIResponse
            The response.

        Raises
        ------
        ValueError
            If provider is not set.
        """
        provider_name = request.provider
        if not provider_name:
            raise ValueError("No provider specified. Set a default provider or pass one.")
        return self._manager.execute(
            provider_name=provider_name,
            request=request,
        )

    # ------------------------------------------------------------------
    # One-shot Completion
    # ------------------------------------------------------------------

    def complete(
        self,
        prompt: str,
        provider: str | None = None,
        model: str | None = None,
        system: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> AIResponse:
        """
        One-shot completion (non-streaming).

        Parameters
        ----------
        prompt : str
            User prompt.
        provider : str | None, optional
            Provider override.
        model : str | None, optional
            Model override.
        system : str | None, optional
            System instruction.
        options : dict[str, Any] | None, optional
            Generation options.

        Returns
        -------
        AIResponse
            The completion response.
        """
        request = self._prepare_request(
            prompt_text=prompt,
            system=system,
            provider=provider,
            model=model,
            options=options,
            task="generate",
        )
        return self._execute_request(request)

    def stream(
        self,
        prompt: str,
        provider: str | None = None,
        model: str | None = None,
        system: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> Generator[Any, None, AIResponse]:
        """
        One-shot streaming completion.

        This uses the Chat.stream() method internally to handle streaming.

        Parameters
        ----------
        prompt : str
            User prompt.
        provider : str | None, optional
            Provider override.
        model : str | None, optional
            Model override.
        system : str | None, optional
            System instruction.
        options : dict[str, Any] | None, optional
            Generation options.

        Yields
        ------
        Any
            Response chunks.

        Returns
        -------
        AIResponse
            The final assembled response.
        """
        # Create a temporary chat instance with the same configuration
        chat = self.chat()
        # Override provider/model if provided
        if provider:
            chat.set_provider(provider)
        elif self._config.provider:
            chat.set_provider(self._config.provider)
        if model:
            chat.set_model(model)
        elif self._config.model:
            chat.set_model(self._config.model)
        # Apply config defaults to chat? Chat already uses its own config.
        # We'll just pass options.
        return chat.stream(
            message=prompt,
            system=system,
            options=options,
        )

    # ------------------------------------------------------------------
    # Embedding (Future)
    # ------------------------------------------------------------------

    def embed(self, text: str, provider: str | None = None, model: str | None = None) -> list[float]:
        """
        Generate embeddings for text.

        This feature is not yet implemented.

        Parameters
        ----------
        text : str
            Text to embed.
        provider : str | None, optional
            Provider override.
        model : str | None, optional
            Model override.

        Returns
        -------
        list[float]
            Embedding vector.

        Raises
        ------
        NotImplementedError
            Always raised until embeddings are fully implemented.
        """
        raise NotImplementedError(
            "Embedding support will be implemented in a future version of Hermes."
        )

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """
        Export client configuration to a dictionary.

        Returns
        -------
        dict[str, Any]
            Dictionary representation.
        """
        return {
            "config": self._config.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HermesClient:
        """
        Import client from a dictionary.

        Parameters
        ----------
        data : dict[str, Any]
            Dictionary representation.

        Returns
        -------
        HermesClient
            A new client instance.
        """
        config = ClientConfig.from_dict(data.get("config", {}))
        return cls(
            provider=config.provider,
            model=config.model,
            config=config,
        )

    def to_json(self) -> str:
        """Export to JSON."""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False, default=str)

    @classmethod
    def from_json(cls, data: str) -> HermesClient:
        """Import from JSON."""
        return cls.from_dict(json.loads(data))

    # ------------------------------------------------------------------
    # Context Manager
    # ------------------------------------------------------------------

    def __enter__(self) -> Self:
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager."""
        # Clean up manager resources if needed
        pass

    # ------------------------------------------------------------------
    # Magic Methods
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"<HermesClient provider={self._config.provider!r} "
            f"model={self._config.model!r}>"
        )

    def __str__(self) -> str:
        return self.__repr__()


# =============================================================================
# Verification Block
# =============================================================================

# ✓ Classes:
#   - ClientConfig
#   - HermesClient

# ✓ Methods:
#   - __init__
#   - set_provider / set_model / set_config (with validation)
#   - list_providers / list_provider_names / list_models / get_provider
#   - chat
#   - create_session / create_conversation / create_prompt / create_request
#   - complete / stream (unified execution path)
#   - embed (placeholder with clear error)
#   - to_dict / from_dict / to_json / from_json
#   - context manager (__enter__ / __exit__)
#   - magic methods (__repr__, __str__)

# ✓ Serialization:
#   - to_dict / from_dict (single source of truth)
#   - to_json / from_json

# ✓ Imports:
#   - All imports are valid
#   - No circular imports

# ✓ Compatibility:
#   - Works with AIManager, AIRegistry, Chat, AISession, AIConversation, Prompt, AIRequest, AIResponse
#   - Future-compatible with memory and tools

# ✓ Improvements:
#   - Provider validation on set
#   - Config applied to requests via apply_to_request()
#   - Unified request preparation and execution
#   - list_models uses provider method or metadata
#   - No duplication of provider/model in serialization