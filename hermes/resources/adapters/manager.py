"""
===============================================================================
Hermes Adapter Manager
===============================================================================

High-level interface for Runtime Adapter Objects.

Coordinates:

    • Validation
    • Registration
    • Discovery
    • Lookup

The manager is the ONLY public entrypoint for adapters.

===============================================================================
"""

from __future__ import annotations

from pathlib import Path

from .adapter import RuntimeAdapter
from .loader import AdapterLoader
from .registry import AdapterRegistry
from .validator import AdapterValidator


class AdapterManager:
    """
    High-level Runtime Adapter manager.
    """

    def __init__(self) -> None:

        self._registry = AdapterRegistry()

        self._validator = AdapterValidator()

        self._loader = AdapterLoader()

    # ------------------------------------------------------------------

    def register(
        self,
        adapter: RuntimeAdapter,
    ) -> None:
        """
        Validate and register an adapter.
        """

        self._validator.validate(adapter)

        self._registry.register(adapter)

    # ------------------------------------------------------------------

    def discover(
        self,
        directory: Path,
    ) -> None:
        """
        Discover Runtime Adapters from disk.
        """

        adapters = self._loader.load(directory)

        for adapter in adapters:

            self.register(adapter)

    # ------------------------------------------------------------------

    def get(
        self,
        adapter_id: str,
    ) -> RuntimeAdapter | None:

        return self._registry.get(adapter_id)

    # ------------------------------------------------------------------

    def exists(
        self,
        adapter_id: str,
    ) -> bool:

        return self._registry.exists(adapter_id)

    # ------------------------------------------------------------------

    def all(
        self,
    ) -> list[RuntimeAdapter]:

        return self._registry.all()

    # ------------------------------------------------------------------

    def enabled(
        self,
    ) -> list[RuntimeAdapter]:

        return self._registry.enabled()

    # ------------------------------------------------------------------

    def unregister(
        self,
        adapter_id: str,
    ) -> None:

        self._registry.unregister(adapter_id)

    # ------------------------------------------------------------------

    def clear(
        self,
    ) -> None:

        self._registry.clear()