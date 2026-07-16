"""
===============================================================================
Hermes Runtime State

Represents the current runtime status.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class RuntimeState:
    """
    Global runtime state.

    This is shared across the Runtime and all registered
    subsystems.
    """

    booted: bool = False

    shutting_down: bool = False

    ready: bool = False

    started_at: Optional[datetime] = None

    active_provider: str = ""

    active_model: str = ""

    active_session: str = ""

    last_error: str = ""