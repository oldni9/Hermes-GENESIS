"""
===============================================================================
Hermes Runtime Lifecycle
===============================================================================
"""

from __future__ import annotations

from hermes.runtime.runtime import Runtime


class RuntimeLifecycle:
    """
    Controls Runtime startup and shutdown.
    """

    def __init__(self, runtime: Runtime):

        self.runtime = runtime

    def start(self) -> None:

        self.runtime.boot()

    def stop(self) -> None:

        self.runtime.shutdown()
