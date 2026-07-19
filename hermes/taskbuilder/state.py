"""
===============================================================================
Hermes Task Builder State

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from enum import Enum


class TaskBuilderState(str, Enum):

    IDLE = "idle"

    BUILDING = "building"

    COMPLETE = "complete"

    FAILED = "failed"
