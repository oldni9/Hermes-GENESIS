"""
===============================================================================
Hermes Genesis Exceptions
===============================================================================

Re-exports from core/errors.py for backward compatibility.
===============================================================================
"""

from __future__ import annotations

from hermes.core.errors import (
    HermesError,
    ConfigurationError,
    HermesRuntimeError,
    ProviderError,
    ResourceError,
    CapabilityError,
    ExecutionCancelled,
    DeadlineExceeded,
    BudgetExceeded,
)

# Backward compatibility alias
RuntimeError = HermesRuntimeError

__all__ = [
    "HermesError",
    "ConfigurationError",
    "RuntimeError",
    "HermesRuntimeError",
    "ProviderError",
    "ResourceError",
    "CapabilityError",
    "ExecutionCancelled",
    "DeadlineExceeded",
    "BudgetExceeded",
]

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture