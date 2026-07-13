"""
===============================================================================
Hermes Execution Exceptions

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations


class ExecutionError(Exception):
    """
    Base execution exception.
    """


class ExecutionValidationError(ExecutionError):
    """
    Invalid execution context.
    """


class ExecutionFailureError(ExecutionError):
    """
    Runtime execution failed.
    """