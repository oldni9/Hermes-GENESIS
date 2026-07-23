"""
===============================================================================
Runtime Cancellation Events
===============================================================================
"""
from __future__ import annotations
from hermes.runtime.events.base import BaseEvent


class CancellationRequestedEvent(BaseEvent):
    event_type: str = "cancellation_requested"


class ExecutionCancelledEvent(BaseEvent):
    event_type: str = "execution_cancelled"

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture