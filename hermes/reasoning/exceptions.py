"""
===============================================================================
Hermes Reasoning Exceptions

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations


class ReasoningError(Exception):
    """
    Base reasoning exception.
    """


class GraphConstructionError(ReasoningError):
    """
    Failed to construct execution graph.
    """


class GraphValidationError(ReasoningError):
    """
    Execution graph is invalid.
    """