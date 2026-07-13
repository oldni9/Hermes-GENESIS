# hermes/providers/exceptions.py

"""
===============================================================================
Hermes Provider Exceptions

Exceptions raised by the Provider subsystem.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations


class ProviderError(Exception):
    """
    Base provider exception.
    """


class ProviderNotFound(ProviderError):
    """
    Raised when a provider cannot be located.
    """


class ProviderDisabled(ProviderError):
    """
    Raised when attempting to use a disabled provider.
    """


class ProviderExecutionError(ProviderError):
    """
    Raised when provider execution fails.
    """