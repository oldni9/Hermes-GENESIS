"""
===============================================================================
Hermes Core Errors
===============================================================================

Canonical error hierarchy for Hermes.
===============================================================================
"""

from __future__ import annotations


class HermesError(Exception):
    """Base exception for Hermes."""


class ConfigurationError(HermesError):
    """Invalid configuration."""


class HermesRuntimeError(HermesError):
    """Base runtime failure."""


class ProviderError(HermesError):
    """Provider failure."""


class ResourceError(HermesError):
    """Resource failure."""


class CapabilityError(HermesError):
    """Capability failure."""


# =============================================================================
# Execution Lifecycle Exceptions
# =============================================================================

class ExecutionCancelled(HermesRuntimeError):
    """Raised when execution is cancelled via CancellationToken."""


class DeadlineExceeded(HermesRuntimeError):
    """Raised when execution exceeds its timeout limit."""


class BudgetExceeded(HermesRuntimeError):
    """Raised when execution exceeds its token budget."""


# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture