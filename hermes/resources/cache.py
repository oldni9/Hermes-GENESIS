"""
===============================================================================
Hermes Runtime Resource Cache

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.resources.resource import RuntimeResource


class RuntimeResourceCache:
    """
    Runtime cache for loaded resources.
    """

    def __init__(self) -> None:

        self._cache: dict[str, RuntimeResource] = {}

    # --------------------------------------------------------------

    def add(
        self,
        resource: RuntimeResource,
    ) -> None:

        self._cache[resource.name] = resource

    # --------------------------------------------------------------

    def get(
        self,
        name: str,
    ) -> RuntimeResource | None:

        return self._cache.get(name)

    # --------------------------------------------------------------

    def clear(
        self,
    ) -> None:

        self._cache.clear()

    # --------------------------------------------------------------

    def values(
        self,
    ) -> list[RuntimeResource]:

        return list(self._cache.values())