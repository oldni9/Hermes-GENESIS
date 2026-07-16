"""
===============================================================================
Hermes Dependency Container

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.providers.registry import ProviderRegistry


class HermesContainer:
    """
    Global dependency container.

    Every singleton in Hermes lives here.
    """

    def __init__(self) -> None:

        self.provider_registry = ProviderRegistry()

        self.provider_manager = None

        self.execution_service = None

        self.kernel_executor = None

        self.runtime_engine = None