"""
===============================================================================
Hermes Task Builder Exceptions

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations


class TaskBuilderError(Exception):
    """
    Base Task Builder exception.
    """


class TaskMappingError(TaskBuilderError):
    """
    Failed to map execution node.
    """


class TaskValidationError(TaskBuilderError):
    """
    Invalid execution node.
    """
