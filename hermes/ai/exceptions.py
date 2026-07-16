"""
===============================================================================
Hermes AI Exceptions

Common exceptions used throughout the Hermes AI subsystem.

These exceptions are provider-independent.

They are capability-independent.

They do NOT execute AI.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations


class AIError(Exception):
    """
    Base exception for all AI-related errors.

    Every AI exception should inherit from this class.
    """


# ---------------------------------------------------------------------------


class AIProviderError(AIError):
    """
    Raised when an AI provider encounters an error.
    """


# ---------------------------------------------------------------------------


class AIProviderNotFoundError(AIError):
    """
    Raised when an AI provider cannot be found.
    """


# ---------------------------------------------------------------------------


class AICapabilityError(AIError):
    """
    Raised when no provider supports a required capability.
    """


# ---------------------------------------------------------------------------


class AIRequestError(AIError):
    """
    Raised when an AI request is invalid.
    """


# ---------------------------------------------------------------------------


class AIResponseError(AIError):
    """
    Raised when an AI provider returns an invalid response.
    """


# ---------------------------------------------------------------------------


class AITimeoutError(AIError):
    """
    Raised when an AI request exceeds its timeout.
    """


# ---------------------------------------------------------------------------


class AIAuthenticationError(AIProviderError):
    """
    Raised when provider authentication fails.
    """


# ---------------------------------------------------------------------------


class AIRateLimitError(AIProviderError):
    """
    Raised when a provider rate limit has been exceeded.
    """


# ---------------------------------------------------------------------------


class AIConnectionError(AIProviderError):
    """
    Raised when a provider cannot be reached.
    """


# ---------------------------------------------------------------------------


class AIModelNotFoundError(AIProviderError):
    """
    Raised when a requested model does not exist.
    """


# ---------------------------------------------------------------------------


class AIExecutionError(AIProviderError):
    """
    Raised when provider execution fails.
    """


# ---------------------------------------------------------------------------


class AICacheError(AIError):
    """
    Raised when cache operations fail.
    """


# ---------------------------------------------------------------------------


class AISessionError(AIError):
    """
    Raised when session operations fail.
    """