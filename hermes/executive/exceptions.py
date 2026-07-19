"""
===============================================================================
Hermes Executive Exceptions

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations


class ExecutiveError(Exception):
    """
    Base Executive exception.
    """


class ExecutivePlanningError(ExecutiveError):
    """
    Planning failed.
    """


class ExecutiveExecutionError(ExecutiveError):
    """
    Execution failed.
    """
