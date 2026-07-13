"""
===============================================================================
Hermes Scheduler State

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from enum import Enum


class SchedulerState(str, Enum):

    IDLE = "idle"

    READY = "ready"

    RUNNING = "running"

    COMPLETE = "complete"

    FAILED = "failed"