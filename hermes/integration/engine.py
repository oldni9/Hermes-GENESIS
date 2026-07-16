"""
===============================================================================
Hermes Integration Engine

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.kernel import KernelExecutor

from hermes.integration.context import IntegrationContext
from hermes.integration.result import IntegrationResult


class IntegrationEngine:
    """
    Integration layer.

    Receives an IntegrationContext.

    Uses the Kernel to execute AI work.

    Returns IntegrationResults.
    """

    def __init__(
        self,
        kernel: KernelExecutor,
    ) -> None:

        self.kernel = kernel

    # ------------------------------------------------------------------

    def process(
        self,
        context: IntegrationContext,
    ) -> list[IntegrationResult]:

        provider_result = self.kernel.execute(
            context.prompt,
        )

        return [

            IntegrationResult(

                output=provider_result.text,

                metadata={},

            )

        ]