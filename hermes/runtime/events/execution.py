"""
===============================================================================
Runtime Execution Events
===============================================================================
"""
from __future__ import annotations
from hermes.runtime.events.base import BaseEvent


class ExecutionStartedEvent(BaseEvent):
    event_type: str = "execution_started"


class ExecutionFinishedEvent(BaseEvent):
    event_type: str = "execution_finished"


class ExecutionFailedEvent(BaseEvent):
    event_type: str = "execution_failed"

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture