"""
===============================================================================
Hermes Resource Exceptions

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations


class ResourceError(Exception):
    """
    Base resource exception.
    """


class ResourceNotFound(ResourceError):
    """
    Resource does not exist.
    """


class ResourceValidationError(ResourceError):
    """
    Invalid runtime resource.
    """


class ResourceLoadError(ResourceError):
    """
    Resource failed to load.
    """