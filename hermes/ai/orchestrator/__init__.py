"""
===============================================================================
Hermes AI Orchestrator

Core orchestration layer for AI execution (Sprint 1).

Author:
    Aryan + ChatGPT
===============================================================================
"""

from hermes.ai.orchestrator.constants import (
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TIMEOUT,
    DEFAULT_RETRY_ATTEMPTS,
    DEFAULT_USE_CACHE,
)
from hermes.ai.orchestrator.execution_plan import ExecutionPlan
from hermes.ai.orchestrator.exceptions import (
    OrchestratorError,
    ValidationError,
    ProviderSelectionError,
    ExecutionError,
    RetryExhaustedError,
)
from hermes.ai.orchestrator.orchestrator import AIOrchestrator
from hermes.ai.orchestrator.provider_selector import ProviderSelector
from hermes.ai.orchestrator.response_processor import ResponseProcessor
from hermes.ai.orchestrator.retry_policy import RetryPolicy

__all__ = [
    # Constants
    "DEFAULT_TEMPERATURE",
    "DEFAULT_MAX_TOKENS",
    "DEFAULT_TIMEOUT",
    "DEFAULT_RETRY_ATTEMPTS",
    "DEFAULT_USE_CACHE",
    # Main
    "AIOrchestrator",
    "ExecutionPlan",
    # Selectors & Processors
    "ProviderSelector",
    "ResponseProcessor",
    "RetryPolicy",
    # Exceptions
    "OrchestratorError",
    "ValidationError",
    "ProviderSelectionError",
    "ExecutionError",
    "RetryExhaustedError",
]
