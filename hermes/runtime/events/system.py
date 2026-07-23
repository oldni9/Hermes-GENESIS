"""
===============================================================================
Runtime System Events
===============================================================================

Sprint 17A.5 Final Freeze:
- Restored payload consistency by using a typed ReplayGapPayload model.
===============================================================================
"""
from __future__ import annotations

from typing import Any, Dict
from pydantic import BaseModel, Field

from hermes.runtime.events.base import BaseEvent


class ReplayGapPayload(BaseModel):
    """Payload schema for ReplayGapEvent."""
    requested_sequence: int
    oldest_available_sequence: int
    latest_available_sequence: int
    missing_event_count: int


class ReplayGapEvent(BaseEvent):
    """
    Emitted when a client requests a replay sequence that is older than 
    the events currently retained in the ring buffer.
    """
    event_type: str = "replay_gap"
    payload: ReplayGapPayload

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture