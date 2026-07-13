"""
===============================================================================
Hermes Adapter Exceptions
===============================================================================
"""

from __future__ import annotations


class AdapterError(Exception):
    """
    Base adapter exception.
    """


class AdapterAlreadyExists(AdapterError):
    """
    Adapter already registered.
    """


class AdapterNotFound(AdapterError):
    """
    Adapter could not be found.
    """


class AdapterValidationError(AdapterError):
    """
    Adapter configuration is invalid.
    """