"""
===============================================================================
Hermes AI Orchestrator Constants

Default values and constants for the orchestrator layer.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

# ------------------------------------------------------------------
# Defaults
# ------------------------------------------------------------------

DEFAULT_TEMPERATURE: float = 0.7
DEFAULT_MAX_TOKENS: int = 4096
DEFAULT_TIMEOUT: float = 60.0
DEFAULT_RETRY_ATTEMPTS: int = 3
DEFAULT_RETRY_DELAY: float = 1.0
DEFAULT_MAX_RETRY_DELAY: float = 30.0
DEFAULT_USE_CACHE: bool = True

# ------------------------------------------------------------------
# Retry Limits
# ------------------------------------------------------------------

MIN_RETRY_DELAY: float = 0.1
MAX_RETRY_ATTEMPTS: int = 5
