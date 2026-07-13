"""
===============================================================================
Hermes Bootstrap

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.bootstrap.container import HermesContainer


class HermesBootstrap:
    """
    Responsible for constructing the Hermes dependency graph.

    Future versions will build every subsystem here.

    Runtime
        ↓
    Router
        ↓
    Providers
        ↓
    Kernel
        ↓
    Memory
        ↓
    Tools
    """

    def __init__(self) -> None:

        self.container = HermesContainer()

    # ------------------------------------------------------------------

    def build(self) -> HermesContainer:
        """
        Build the dependency graph.

        Genesis:
            Currently returns an empty container.

        Later:
            Every subsystem will be created here.
        """

        return self.container