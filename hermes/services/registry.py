"""
===============================================================================
Hermes Service Registry

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.services.service import BaseService


class ServiceRegistry:

    def __init__(self):

        self._services: dict[str, BaseService] = {}

    # ------------------------------------------------------------

    def register(

        self,

        service: BaseService,

    ) -> None:

        self._services[service.name.lower()] = service

    # ------------------------------------------------------------

    def unregister(

        self,

        name: str,

    ) -> None:

        self._services.pop(

            name.lower(),

            None,

        )

    # ------------------------------------------------------------

    def get(

        self,

        name: str,

    ) -> BaseService | None:

        return self._services.get(

            name.lower(),

        )

    # ------------------------------------------------------------

    def exists(

        self,

        name: str,

    ) -> bool:

        return name.lower() in self._services

    # ------------------------------------------------------------

    def services(self):

        return list(

            self._services.values()

        )

    # ------------------------------------------------------------

    def names(self):

        return sorted(

            self._services.keys()

        )

    # ------------------------------------------------------------

    def clear(self):

        self._services.clear()

    # ------------------------------------------------------------

    def __len__(self):

        return len(

            self._services

        )

    # ------------------------------------------------------------

    def __iter__(self):

        return iter(

            self._services.values()

        )