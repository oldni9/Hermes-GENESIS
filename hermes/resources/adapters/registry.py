"""
===============================================================================
Hermes Adapter Registry
===============================================================================

Stores Runtime Adapter Objects.

The registry owns adapter registration and lookup.

===============================================================================
"""

from __future__ import annotations

from .adapter import RuntimeAdapter
from .exceptions import AdapterAlreadyExists


class AdapterRegistry:
    """
    Registry for Runtime Adapters.
    """

    def __init__(self) -> None:

        self._adapters: dict[str, RuntimeAdapter] = {}

    # ------------------------------------------------------------------

    def register(
        self,
        adapter: RuntimeAdapter,
    ) -> None:
        """
        Register a Runtime Adapter.
        """

        if adapter.id in self._adapters:

            raise AdapterAlreadyExists(f"Adapter '{adapter.id}' already exists.")

        self._adapters[adapter.id] = adapter

    # ------------------------------------------------------------------

    def unregister(
        self,
        adapter_id: str,
    ) -> None:

        self._adapters.pop(adapter_id, None)

    # ------------------------------------------------------------------

    def get(
        self,
        adapter_id: str,
    ) -> RuntimeAdapter | None:

        return self._adapters.get(adapter_id)

    # ------------------------------------------------------------------

    def exists(
        self,
        adapter_id: str,
    ) -> bool:

        return adapter_id in self._adapters

    # ------------------------------------------------------------------

    def all(
        self,
    ) -> list[RuntimeAdapter]:

        return list(self._adapters.values())

    # ------------------------------------------------------------------

    def enabled(
        self,
    ) -> list[RuntimeAdapter]:

        return [adapter for adapter in self._adapters.values() if adapter.enabled]

    # ------------------------------------------------------------------

    def clear(
        self,
    ) -> None:

        self._adapters.clear()
