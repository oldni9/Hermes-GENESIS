"""
===============================================================================
Hermes Genesis Exceptions
===============================================================================

Base exception hierarchy for Hermes.

===============================================================================
"""

from __future__ import annotations


class HermesError(Exception):
    """Base exception for Hermes."""


class ConfigurationError(HermesError):
    """Invalid configuration."""


class RuntimeError(HermesError):
    """Runtime failure."""


class ProviderError(HermesError):
    """Provider failure."""


class ResourceError(HermesError):
    """Resource failure."""


class CapabilityError(HermesError):
    """Capability failure."""