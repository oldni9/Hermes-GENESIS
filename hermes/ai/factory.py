"""
===============================================================================
Hermes AI Factory

Creates and registers AI providers.

The factory is responsible for constructing provider instances.

It does NOT execute AI.

It does NOT cache.

It does NOT route requests.

It only creates providers and registers them into an AIRegistry.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from typing import Callable

from hermes.ai.provider import BaseAIProvider
from hermes.ai.registry import AIRegistry


class AIFactory:
    """
    Factory for AI providers.

    The factory owns provider construction.

    It never executes providers.

    It never routes requests.

    It only creates and registers providers.
    """

    def __init__(
        self,
        registry: AIRegistry,
    ) -> None:
        """
        Initialize the provider factory.

        Parameters
        ----------
        registry : AIRegistry
            Registry that receives newly created providers.
        """

        self._registry = registry

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def registry(
        self,
    ) -> AIRegistry:
        """
        Return the underlying registry.
        """

        return self._registry

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def create(
        self,
        builder: Callable[..., BaseAIProvider],
        *args,
        **kwargs,
    ) -> BaseAIProvider:
        """
        Construct and register a provider.

        Parameters
        ----------
        builder : Callable[..., BaseAIProvider]
            Provider constructor.
        *args
            Positional arguments passed to the constructor.
        **kwargs
            Keyword arguments passed to the constructor.

        Returns
        -------
        BaseAIProvider
            Newly created provider.
        """

        provider = builder(
            *args,
            **kwargs,
        )

        self._registry.register(provider)

        return provider

    # ------------------------------------------------------------------

    def register(
        self,
        provider: BaseAIProvider,
    ) -> None:
        """
        Register an already-created provider.

        Parameters
        ----------
        provider : BaseAIProvider
            Provider instance.
        """

        self._registry.register(provider)

    # ------------------------------------------------------------------

    def unregister(
        self,
        name: str,
    ) -> None:
        """
        Remove a provider.

        Parameters
        ----------
        name : str
            Provider name.
        """

        self._registry.unregister(name)

    # ------------------------------------------------------------------

    def clear(
        self,
    ) -> None:
        """
        Remove every registered provider.
        """

        self._registry.clear()

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def providers(
        self,
    ) -> tuple[BaseAIProvider, ...]:
        """
        Return all registered providers.
        """

        return self._registry.providers()

    # ------------------------------------------------------------------

    def names(
        self,
    ) -> list[str]:
        """
        Return all registered provider names.
        """

        return self._registry.names()

    # ------------------------------------------------------------------

    def exists(
        self,
        name: str,
    ) -> bool:
        """
        Check whether a provider exists.

        Parameters
        ----------
        name : str
            Provider name.

        Returns
        -------
        bool
            True if provider exists.
        """

        return self._registry.exists(name)

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

    def __bool__(
        self,
    ) -> bool:
        """
        Return True if at least one provider exists.
        """

        return bool(self._registry)
