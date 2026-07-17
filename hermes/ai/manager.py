"""
===============================================================================
Hermes AI Manager

Central orchestrator for every AI provider.

The manager coordinates providers through AIRegistry.

It NEVER performs AI itself.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from typing import Any

from hermes.ai.context import AIContext
from hermes.ai.provider import BaseAIProvider
from hermes.ai.registry import AIRegistry
from hermes.ai.request import AIRequest
from hermes.ai.response import AIResponse


class AIManager:
    """
    Central orchestrator for AI providers.

    Responsibilities
    ----------------
    - Register and unregister providers
    - Execute AI requests through providers
    - Coordinate batch operations
    - Manage provider lifecycle (startup/shutdown)

    The manager never performs AI itself.
    It delegates to providers through the registry.
    """

    def __init__(
        self,
        registry: AIRegistry,
    ) -> None:
        """
        Initialize the AI manager.

        Parameters
        ----------
        registry : AIRegistry
            The registry to use for provider storage.
        """
        self._registry = registry

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def registry(self) -> AIRegistry:
        """Return the underlying AI registry."""
        return self._registry

    # ------------------------------------------------------------------
    # Registration (Delegated to Registry)
    # ------------------------------------------------------------------

    def register(
        self,
        provider: BaseAIProvider,
    ) -> None:
        """Register an AI provider."""
        self._registry.register(provider)

    def unregister(
        self,
        name: str,
    ) -> None:
        """Remove a provider by name."""
        self._registry.unregister(name)

    def provider(
        self,
        name: str,
    ) -> BaseAIProvider:
        """Return a provider by name."""
        return self._registry.get(name)

    def providers(
        self,
    ) -> tuple[BaseAIProvider, ...]:
        """Return all registered providers."""
        return self._registry.providers()

    def provider_names(
        self,
    ) -> list[str]:
        """Return all registered provider names."""
        return self._registry.names()

    def exists(
        self,
        name: str,
    ) -> bool:
        """Check whether a provider exists."""
        return self._registry.exists(name)

    def empty(
        self,
    ) -> bool:
        """Return True if no providers are registered."""
        return self._registry.empty()

    def capabilities(
        self,
    ) -> list[str]:
        """Return all capabilities supported by registered providers."""
        return self._registry.capabilities()

    def supports(
        self,
        capability: str,
    ) -> list[BaseAIProvider]:
        """Return all providers that support the given capability."""
        return self._registry.supports(capability)

    def default(
        self,
        capability: str,
    ) -> BaseAIProvider | None:
        """Return the default provider for the given capability."""
        return self._registry.default(capability)

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def execute(
        self,
        provider_name: str,
        request: AIRequest,
        context: AIContext | None = None,
    ) -> AIResponse:
        """
        Execute a request using a specific provider.

        Parameters
        ----------
        provider_name : str
            Name of the provider to use.
        request : AIRequest
            The request to execute.
        context : AIContext | None, optional
            Optional execution context.

        Returns
        -------
        AIResponse
            The provider's response.

        Raises
        ------
        KeyError
            If provider does not exist.
        """
        provider = self._registry.get(provider_name)
        return provider.execute(
            request,
            context=context,
        )

    def execute_default(
        self,
        capability: str,
        request: AIRequest,
        context: AIContext | None = None,
    ) -> AIResponse:
        """
        Execute a request using the default provider for the capability.

        Parameters
        ----------
        capability : str
            Capability required.
        request : AIRequest
            The request to execute.
        context : AIContext | None, optional
            Optional execution context.

        Returns
        -------
        AIResponse
            The provider's response.

        Raises
        ------
        RuntimeError
            If no provider supports the capability.
        """
        provider = self._registry.default(capability)

        if provider is None:
            raise RuntimeError(
                f"No AI provider supports capability '{capability}'."
            )

        return provider.execute(
            request,
            context=context,
        )

    def batch_execute(
        self,
        provider_name: str,
        requests: list[AIRequest],
        context: AIContext | None = None,
    ) -> list[AIResponse]:
        """
        Execute multiple requests using a specific provider.

        Delegates to provider.batch_execute().

        Parameters
        ----------
        provider_name : str
            Name of the provider to use.
        requests : list[AIRequest]
            List of requests to execute.
        context : AIContext | None, optional
            Optional execution context.

        Returns
        -------
        list[AIResponse]
            List of responses from the provider.

        Raises
        ------
        KeyError
            If provider does not exist.
        """
        provider = self._registry.get(provider_name)
        return provider.batch_execute(
            requests,
            context=context,
        )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def startup(self) -> None:
        """Start up every registered provider."""
        for provider in self._registry:
            provider.startup()

    def shutdown(self) -> None:
        """Shut down every registered provider."""
        for provider in self._registry:
            provider.shutdown()

    def clear(self) -> None:
        """Shut down all providers and clear the registry."""
        self.shutdown()
        self._registry.clear()

    # ------------------------------------------------------------------
    # Magic Methods
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        """Return the number of registered providers."""
        return len(self._registry)

    def __bool__(self) -> bool:
        """Return True if the manager has at least one provider."""
        return bool(self._registry)

    def __contains__(
        self,
        name: str,
    ) -> bool:
        """Check whether a provider exists."""
        return name in self._registry