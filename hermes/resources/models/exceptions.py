"""
===============================================================================
Hermes Runtime Model Exceptions
===============================================================================
"""

from __future__ import annotations


class ModelError(Exception):
    """Base model exception."""


class ModelNotFound(ModelError):
    """Requested model does not exist."""


class DuplicateModel(ModelError):
    """Duplicate model id."""


class InvalidModel(ModelError):
    """Invalid RuntimeModel."""
