"""
===============================================================================
Hermes AI Registry

Stores every AI provider available inside Hermes.

Examples:

    Gemini
    PaddleOCR
    Tesseract
    Florence2
    Whisper
    Qwen-VL
    MiniCPM
    BLIP
    CLIP

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from typing import Iterable

from hermes.ai.provider import BaseAIProvider


class AIRegistry:
    """
    Registry for AI providers.

    The registry owns provider registration and lookup.

    It does NOT create providers.

    It does NOT execute providers.

    It only stores and retrieves them.
    """

    def __init__(self) -> None:
        """
        Initialize empty registry.
        """

        self._providers: dict[str, BaseAIProvider] = {}

    # ------------------------------------------------------------------

    def register(
        self,
        provider: BaseAIProvider,
    ) -> None:
        """
        Register an AI provider.

        Raises ValueError if duplicate name.

        Parameters
        ----------
        provider : BaseAIProvider
            Provider instance to register.
        """

        name = provider.metadata.name.strip()

        if name in self._providers:

            raise ValueError(f"AI provider '{name}' is already registered.")

        # Normalize the provider's own metadata
        provider.metadata.name = name

        self._providers[name] = provider

    # ------------------------------------------------------------------

    def unregister(
        self,
        name: str,
    ) -> None:
        """
        Remove a provider by name.

        Idempotent.

        Parameters
        ----------
        name : str
            Name of the provider to remove.
        """

        self._providers.pop(name, None)

    # ------------------------------------------------------------------

    def get(
        self,
        name: str,
    ) -> BaseAIProvider:
        """
        Return a provider by name.

        Raises KeyError if missing.

        Parameters
        ----------
        name : str
            Name of the provider.

        Returns
        -------
        BaseAIProvider
            The provider instance.
        """

        return self._providers[name]

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
            Name of the provider.

        Returns
        -------
        bool
            True if provider exists, False otherwise.
        """

        return name in self._providers

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

        return tuple(self._providers.values())

    # ------------------------------------------------------------------

    def names(
        self,
    ) -> list[str]:
        """
        Return all registered provider names.

        Returns
        -------
        list[str]
            List of all provider names.
        """

        return list(self._providers.keys())

    # ------------------------------------------------------------------

    def count(
        self,
    ) -> int:
        """
        Return the number of registered providers.

        Returns
        -------
        int
            Total provider count.
        """

        return len(self._providers)

    # ------------------------------------------------------------------

    def empty(
        self,
    ) -> bool:
        """
        Check whether the registry has no providers.

        Returns
        -------
        bool
            True if registry is empty, False otherwise.
        """

        return len(self._providers) == 0

    # ------------------------------------------------------------------

    def clear(
        self,
    ) -> None:
        """
        Remove every provider.
        """

        self._providers.clear()

    # ------------------------------------------------------------------

    def supports(
        self,
        capability: str,
    ) -> list[BaseAIProvider]:
        """
        Return every provider that supports the given capability.

        Parameters
        ----------
        capability : str
            Capability name (e.g., "vision", "ocr", "speech").

        Returns
        -------
        list[BaseAIProvider]
            Providers that support the capability.
        """

        providers: list[BaseAIProvider] = []

        for provider in self._providers.values():

            if provider.supports(capability):

                providers.append(provider)

        return providers

    # ------------------------------------------------------------------

    def capabilities(
        self,
    ) -> list[str]:
        """
        Return sorted unique capabilities across all providers.

        Returns
        -------
        list[str]
            Sorted list of all supported capabilities.
        """

        capabilities: set[str] = set()

        for provider in self._providers.values():

            for capability in provider.metadata.capabilities:

                capabilities.add(capability)

        return sorted(capabilities)

    # ------------------------------------------------------------------

    def default(
        self,
        capability: str,
    ) -> BaseAIProvider | None:
        """
        Return the first provider supporting the given capability.

        Order is determined by registration order.

        Parameters
        ----------
        capability : str
            Capability name.

        Returns
        -------
        BaseAIProvider | None
            First matching provider, or None if none exists.
        """

        for provider in self._providers.values():

            if provider.supports(capability):

                return provider

        return None

    # ------------------------------------------------------------------

    def __len__(
        self,
    ) -> int:
        """
        Return the number of registered providers.
        """

        return len(self._providers)

    # ------------------------------------------------------------------

    def __bool__(
        self,
    ) -> bool:
        """
        Return True if the registry has at least one provider.
        """

        return bool(self._providers)

    # ------------------------------------------------------------------

    def __contains__(
        self,
        name: str,
    ) -> bool:
        """
        Check whether a provider exists.
        """

        return name in self._providers

    # ------------------------------------------------------------------

    def __iter__(
        self,
    ) -> Iterable[BaseAIProvider]:
        """
        Iterate over all registered providers.
        """

        return iter(self._providers.values())
