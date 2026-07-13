"""
===============================================================================
Hermes Scheduler Exceptions
===============================================================================
"""

from __future__ import annotations


class SchedulerError(Exception):
    """
    Base scheduler exception.
    """


class SchedulerAlreadyExists(SchedulerError):
    """
    Scheduler already exists.
    """


class SchedulerNotFound(SchedulerError):
    """
    Scheduler not found.
    """


class SchedulerValidationError(SchedulerError):
    """
    Invalid scheduler policy.
    """