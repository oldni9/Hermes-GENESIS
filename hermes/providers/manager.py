"""
===============================================================================
Hermes Provider Manager

Coordinates provider routing and request dispatch.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.capability.enums import CapabilityType

from hermes.providers.dispatcher import ProviderDispatcher
from hermes.providers.registry import ProviderRegistry
from hermes.providers.request import ProviderRequest
from hermes.providers.result import ProviderResult

from hermes.router.engine import RoutingEngine


class ProviderManager:
    """
    High-level provider execution service.

    Responsibilities

    • Determine the best provider.
    • Dispatch the request.
    • Return the provider result.
    """

    def __init__(
        self,
        registry: ProviderRegistry,
    ) -> None:

        self.registry = registry

        self.router = RoutingEngine(
            registry,
        )

        self.dispatcher = ProviderDispatcher()

    # ------------------------------------------------------------------

    def execute(
        self,
        request: ProviderRequest,
        capability: CapabilityType | None = None,
    ) -> ProviderResult:

        provider = self.router.route()

        return self.dispatcher.dispatch(
            provider,
            request,
        )