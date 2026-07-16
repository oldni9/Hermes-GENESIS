"""
===============================================================================
Hermes Runtime Engine

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.execution import ExecutionService

from hermes.response import Response


class RuntimeEngine:
    """
    Hermes Runtime Engine.

    Runtime is responsible for:

        User Prompt
              ↓
        ExecutionService
              ↓
         ProviderManager
              ↓
           AI Provider
              ↓
            Response
    """

    def __init__(

        self,

        execution: ExecutionService,

    ) -> None:

        self.execution = execution

    # ------------------------------------------------------------------

    def execute(

        self,

        prompt: str,

    ) -> Response:

        result = self.execution.execute(

            prompt,

        )

        return Response(

            text=result.text,

            data=result,

        )