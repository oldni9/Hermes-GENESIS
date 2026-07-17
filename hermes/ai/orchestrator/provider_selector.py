"""
===============================================================================
Hermes AI Provider Selector

Selects provider and model for a request.

Uses AIRouter for routing decisions.
Capability-agnostic.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.ai.provider import BaseAIProvider
from hermes.ai.registry import AIRegistry
from hermes.ai.request import AIRequest
from hermes.ai.orchestrator.exceptions import ProviderSelectionError


class ProviderSelector:
    """
    Selects provider and model for a request.

    Uses AIRouter for routing decisions.
    """

    def __init__(self, registry: AIRegistry) -> None:
        self._registry = registry

    @property
    def registry(self) -> AIRegistry:
        return self._registry

    def select(
        self,
        request: AIRequest,
        preferred_provider: str | None = None,
        preferred_model: str | None = None,
    ) -> tuple[BaseAIProvider, str | None]:
        """
        Select a provider and model for the request.

        Parameters
        ----------
        request : AIRequest
            The request to route.
        preferred_provider : str | None, optional
            Explicit provider override.
        preferred_model : str | None, optional
            Explicit model override.

        Returns
        -------
        tuple[BaseAIProvider, str | None]
            (selected provider, selected model)

        Raises
        ------
        ProviderSelectionError
            If no suitable provider is found.
        """
        task = request.task or "chat"

        # 1. Explicit provider requested
        if preferred_provider:
            try:
                provider = self._registry.get(preferred_provider)
            except KeyError:
                raise ProviderSelectionError(
                    f"Provider '{preferred_provider}' not found."
                )
            return provider, preferred_model

        # 2. Route based on capability
        provider = self._registry.default(task)
        if provider is None:
            # Fallback: try all providers
            for p in self._registry.providers():
                if p.supports(task):
                    provider = p
                    break

        if provider is None:
            raise ProviderSelectionError(
                f"No provider supports capability '{task}'."
            )

        # 3. Determine model
        model = preferred_model or (request.model if request.model else None)

        return provider, model