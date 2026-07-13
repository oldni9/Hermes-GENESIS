"""
===============================================================================
Hermes Runtime Resource Registry

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.resources.resource import RuntimeResource


class RuntimeResourceRegistry:
    """
    Global runtime resource registry.

    Stores every loaded runtime object.
    """

    def __init__(self) -> None:

        self._resources: dict[str, RuntimeResource] = {}

    # --------------------------------------------------------------

    def register(
        self,
        resource: RuntimeResource,
    ) -> None:

        self._resources[resource.name] = resource

    # --------------------------------------------------------------

    def get(
        self,
        name: str,
    ) -> RuntimeResource | None:

        return self._resources.get(name)

    # --------------------------------------------------------------

    def all(
        self,
    ) -> list[RuntimeResource]:

        return list(self._resources.values())