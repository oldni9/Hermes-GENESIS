"""
===============================================================================
Hermes Runtime
===============================================================================
"""

from __future__ import annotations

from datetime import datetime

from hermes.runtime.context import RuntimeContext
from hermes.runtime.registry import RuntimeRegistry
from hermes.runtime.session import RuntimeSession
from hermes.runtime.state import RuntimeState


class Runtime:
    """
    Main Hermes Runtime.
    """

    def __init__(self) -> None:

        self.state = RuntimeState()

        self.session = RuntimeSession()

        self.context = RuntimeContext()

        self.registry = RuntimeRegistry()

    # ---------------------------------------------------------

    def boot(self) -> None:

        self.state.booted = True

        self.state.ready = True

        self.state.started_at = datetime.utcnow()

    # ---------------------------------------------------------

    def shutdown(self) -> None:

        self.state.shutting_down = True

        self.state.ready = False
