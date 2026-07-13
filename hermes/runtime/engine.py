"""
===============================================================================
Hermes Runtime Engine

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.integration.context import IntegrationContext
from hermes.integration.engine import IntegrationEngine
from hermes.response import Response


class RuntimeEngine:
    """
    Hermes Runtime Engine.
    """

    def __init__(self) -> None:

        self.integration = IntegrationEngine()

    # ------------------------------------------------------------------

    def execute(
        self,
        prompt: str,
    ) -> Response:

        context = IntegrationContext(
            prompt=prompt,
            metadata={},
        )

        results = self.integration.process(
            context,
        )

        outputs = []

        for result in results:

            if result.output is not None:

                outputs.append(
                    str(result.output),
                )

        text = "\n".join(outputs)

        if not text:

            text = "Execution completed."

        return Response(
            text=text,
            data=results,
        )