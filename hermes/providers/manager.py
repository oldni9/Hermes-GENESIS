"""
===============================================================================
Hermes Provider Manager

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.capability.enums import CapabilityType

from hermes.providers.dispatcher import ProviderDispatcher
from hermes.providers.request import ProviderRequest
from hermes.providers.result import ProviderResult

from hermes.router.engine import RoutingEngine


class ProviderManager:
    """
    High level provider execution.

    Router chooses the best route.

    Dispatcher executes the request.
    """

    def __init__(self) -> None:

        self.router = RoutingEngine()

        self.dispatcher = ProviderDispatcher()

    # ------------------------------------------------------------------

    def execute(
        self,
        request: ProviderRequest,
        capability: CapabilityType = CapabilityType.CHAT,
    ) -> ProviderResult:

        route = self.router.resolve(
            capability,
        )

        if route is None:

            raise RuntimeError(
                "Routing engine returned no route."
            )

        return self.dispatcher.execute(
            route.provider.name,
            request,
        )