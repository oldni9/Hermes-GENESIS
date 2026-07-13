"""
===============================================================================
Hermes Executive State

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from enum import Enum


class ExecutiveState(str, Enum):

    IDLE = "idle"

    ANALYZING = "analyzing"

    PLANNING = "planning"

    EXECUTING = "executing"

    REFLECTING = "reflecting"

    COMPLETE = "complete"

    FAILED = "failed"