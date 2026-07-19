"""
===============================================================================
Hermes

Main public API.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.response import HermesResponse
from hermes.runtime import RuntimeEngine


class Hermes:
    """
    Public Hermes interface.
    """

    def __init__(self) -> None:
        self.runtime = RuntimeEngine()
        self._started = False
        self._shutdown = False

    # ------------------------------------------------------------------
    def start(self) -> None:
        if self._shutdown:
            raise RuntimeError("Hermes has already been shut down.")
        if self._started:
            return
        self._started = True

    # ------------------------------------------------------------------
    def shutdown(self) -> None:
        if self._shutdown:
            return
        self._started = False
        self._shutdown = True

    # ------------------------------------------------------------------
    def run(self, prompt: str) -> HermesResponse:
        if self._shutdown:
            raise RuntimeError("Cannot execute after Hermes has been shut down.")
        if not self._started:
            self.start()
        return self.runtime.execute(prompt)
