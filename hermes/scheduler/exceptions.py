"""
===============================================================================
Hermes Scheduler Exceptions

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations


class SchedulerError(Exception):
    """
    Base scheduler exception.
    """


class SchedulerExecutionError(SchedulerError):
    """
    Scheduler execution failed.
    """


class SchedulerValidationError(SchedulerError):
    """
    Scheduler validation failed.
    """