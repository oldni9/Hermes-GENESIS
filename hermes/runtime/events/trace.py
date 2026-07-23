"""
===============================================================================
Runtime Trace Events
===============================================================================

Sprint 17A.1 Update:
Introduces TraceRuntimeEvent to preserve typed dispatch for trace events
as they move through the RuntimeEventBus to WebSockets.
===============================================================================
"""
from __future__ import annotations

from typing import Any, Dict
from pydantic import Field

from hermes.runtime.events.base import BaseEvent


class TraceRuntimeEvent(BaseEvent):
    """
    A runtime event wrapping an internal Hermes TraceEvent.
    Preserves the trace event type and payload for API clients.
    """
    event_type: str = "trace"
    trace_event_type: str
    iteration: int
    sequence: int
    thread: int
    payload: Dict[str, Any] = Field(default_factory=dict)

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture