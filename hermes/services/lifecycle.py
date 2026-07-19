"""
===============================================================================
Hermes Service Lifecycle

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.services.registry import ServiceRegistry


class ServiceLifecycle:
    """
    Controls startup and shutdown of registered services.
    """

    def __init__(
        self,
        registry: ServiceRegistry,
    ):

        self.registry = registry

    # ------------------------------------------------------------

    def startup(self):

        for service in self.registry:

            service.startup()

    # ------------------------------------------------------------

    def shutdown(self):

        for service in reversed(self.registry.services()):

            service.shutdown()
