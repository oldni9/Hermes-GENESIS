"""
===============================================================================
Hermes Genesis Application
===============================================================================

Public entry point of the Hermes AI Operating System.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.response import HermesResponse


class Hermes:
    """
    Public Hermes application.
    """

    def __init__(self) -> None:

        self._initialized = True

    @property
    def initialized(self) -> bool:

        return self._initialized

    def run(
        self,
        prompt: str,
    ) -> HermesResponse:
        """
        Execute a request.

        Runtime integration arrives in Sprint G-02.
        """

        return HermesResponse(
            text=f"Hermes Genesis received: {prompt}",
            metadata={
                "engine": "genesis",
            },
        )