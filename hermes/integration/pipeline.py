"""
===============================================================================
Hermes Integration Pipeline
===============================================================================
"""

from __future__ import annotations

from hermes.execution import ExecutionService
from hermes.integration.context import IntegrationContext


class IntegrationPipeline:
    """
    Executes every integration stage.

    Right now there is only ExecutionService,
    but memory/search/plugins can later be inserted.
    """

    def __init__(
        self,
        execution: ExecutionService,
    ) -> None:

        self.execution = execution

    # ---------------------------------------------------------

    def run(
        self,
        context: IntegrationContext,
    ):

        return self.execution.execute(
            context,
        )