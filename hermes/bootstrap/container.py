"""
===============================================================================
Hermes Dependency Container

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations


class HermesContainer:
    """
    Stores every singleton used by Hermes.

    Everything is created once.

    Everything is shared.

    Nothing creates anything itself.
    """

    def __init__(self) -> None:

        self.model_manager = None

        self.provider_manager = None

        self.routing_engine = None

        self.dispatcher = None

        self.kernel_executor = None

        self.runtime_engine = None