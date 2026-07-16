"""
===============================================================================
Hermes Service Manager

Owns every Hermes service.

Responsibilities
----------------
• Registration
• Discovery
• Lifecycle
• Singleton ownership
• Future dependency injection
• Future event publishing

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.services.events import ServiceEvents
from hermes.services.lifecycle import ServiceLifecycle
from hermes.services.registry import ServiceRegistry
from hermes.services.service import BaseService


class ServiceManager:
    """
    Central manager for all Hermes services.

    The manager owns every service instance.

    HermesContainer owns the manager,
    not the individual services.
    """

    def __init__(self):

        self.registry = ServiceRegistry()

        self.lifecycle = ServiceLifecycle(

            self.registry,

        )

    # ------------------------------------------------------------------

    def register(

        self,

        service: BaseService,

    ) -> None:

        self.registry.register(

            service,

        )

    # ------------------------------------------------------------------

    def unregister(

        self,

        name: str,

    ) -> None:

        self.registry.unregister(

            name,

        )

    # ------------------------------------------------------------------

    def get(

        self,

        name: str,

    ) -> BaseService | None:

        return self.registry.get(

            name,

        )

    # ------------------------------------------------------------------

    def exists(

        self,

        name: str,

    ) -> bool:

        return self.registry.exists(

            name,

        )

    # ------------------------------------------------------------------

    def startup(self):

        self.lifecycle.startup()

    # ------------------------------------------------------------------

    def shutdown(self):

        self.lifecycle.shutdown()

    # ------------------------------------------------------------------

    def names(self):

        return self.registry.names()

    # ------------------------------------------------------------------

    def services(self):

        return self.registry.services()

    # ------------------------------------------------------------------

    def clear(self):

        self.registry.clear()

    # ------------------------------------------------------------------

    def __len__(self):

        return len(

            self.registry,

        )

    # ------------------------------------------------------------------

    def __iter__(self):

        return iter(

            self.registry,

        )