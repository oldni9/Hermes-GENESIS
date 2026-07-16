"""
===============================================================================
Hermes AI Router

Chooses which provider should execute a request.

Does NOT execute providers.

Does NOT cache.

Does NOT know OCR, Vision, Speech, LLMs, Embeddings, etc.

Only selects providers using AIRegistry.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.ai.provider import BaseAIProvider
from hermes.ai.registry import AIRegistry


class AIRouter:
    """
    Routes AI requests to appropriate providers.

    The router selects providers based on capability.

    It does not execute.

    It does not cache.

    It only selects.
    """

    def __init__(
        self,
        registry: AIRegistry,
    ) -> None:
        """
        Initialize the AI router.

        Parameters
        ----------
        registry : AIRegistry
            The registry to use for provider lookup.
        """

        self._registry = registry

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def registry(self) -> AIRegistry:
        """
        Return the underlying AI registry.
        """

        return self._registry

    # ------------------------------------------------------------------
    # Routing
    # ------------------------------------------------------------------

    def route(
        self,
        capability: str,
    ) -> BaseAIProvider:
        """
        Select the default provider for a capability.

        Parameters
        ----------
        capability : str
            Capability required.

        Returns
        -------
        BaseAIProvider
            The default provider for the capability.

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

        return provider

    # ------------------------------------------------------------------

    def route_many(
        self,
        capability: str,
    ) -> list[BaseAIProvider]:
        """
        Select all providers that support a capability.

        Parameters
        ----------
        capability : str
            Capability required.

        Returns
        -------
        list[BaseAIProvider]
            All providers supporting the capability.
        """

        return self._registry.supports(capability)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def exists(
        self,
        capability: str,
    ) -> bool:
        """
        Check whether any provider supports a capability.

        Parameters
        ----------
        capability : str
            Capability to check.

        Returns
        -------
        bool
            True if at least one provider supports the capability.
        """

        return bool(self._registry.supports(capability))

    # ------------------------------------------------------------------

    def capabilities(
        self,
    ) -> list[str]:
        """
        Return all capabilities supported by registered providers.

        Returns
        -------
        list[str]
            Sorted list of all supported capabilities.
        """

        return self._registry.capabilities()

    # ------------------------------------------------------------------

    def providers(
        self,
    ) -> tuple[BaseAIProvider, ...]:
        """
        Return all registered providers.

        Returns
        -------
        tuple[BaseAIProvider, ...]
            Tuple of all provider instances.
        """

        return self._registry.providers()

    # ------------------------------------------------------------------

    def provider_names(
        self,
    ) -> list[str]:
        """
        Return all registered provider names.

        Returns
        -------
        list[str]
            List of all provider names.
        """

        return self._registry.names()

    # ------------------------------------------------------------------

    def provider(
        self,
        name: str,
    ) -> BaseAIProvider:
        """
        Return a provider by name.

        Parameters
        ----------
        name : str
            Name of the provider.

        Returns
        -------
        BaseAIProvider
            The provider instance.

        Raises
        ------
        KeyError
            If provider does not exist.
        """

        return self._registry.get(name)

    # ------------------------------------------------------------------
    # Magic Methods
    # ------------------------------------------------------------------

    def __len__(
        self,
    ) -> int:
        """
        Return the number of registered providers.
        """

        return len(self._registry)

    # ------------------------------------------------------------------

    def __contains__(
        self,
        capability: str,
    ) -> bool:
        """
        Check whether any provider supports a capability.
        """

        return self.exists(capability)