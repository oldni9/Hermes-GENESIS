"""
===============================================================================
Hermes Runtime

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.integration.context import IntegrationContext
from hermes.integration.engine import IntegrationEngine


class Runtime:
    """
    Central Hermes Runtime.

    The Runtime owns exactly one IntegrationEngine.

    It no longer coordinates Executive,
    Reasoner,
    Scheduler,
    or Task Builder directly.

    Those responsibilities belong to the
    Integration Engine.
    """

    def __init__(self) -> None:

        self.integration = IntegrationEngine()

    # ------------------------------------------------------------------

    def process(
        self,
        prompt: str,
    ) -> None:
        """
        Execute the complete Hermes pipeline.
        """

        context = IntegrationContext(
            prompt=prompt,
            metadata={},
        )

        self.integration.process(
            context,
        )