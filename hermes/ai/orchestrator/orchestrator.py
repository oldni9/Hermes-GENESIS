"""
===============================================================================
Hermes AI Orchestrator

Core orchestration service for AI execution.

Capability-agnostic.

Responsible ONLY for:
    - Request validation
    - Provider selection
    - Execution with retries
    - Response processing

NO streaming.
NO tool loop.
NO batch execution.
NO cache logic (cache lives in pipeline).

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

import time
from typing import Any

from hermes.ai.manager import AIManager
from hermes.ai.request import AIRequest
from hermes.ai.response import AIResponse
from hermes.core.exceptions import ProviderError

from hermes.ai.orchestrator.execution_plan import ExecutionPlan
from hermes.ai.orchestrator.provider_selector import ProviderSelector
from hermes.ai.orchestrator.retry_policy import RetryPolicy
from hermes.ai.orchestrator.response_processor import ResponseProcessor
from hermes.ai.orchestrator.exceptions import (
    ValidationError,
    RetryExhaustedError,
)


class AIOrchestrator:
    """
    Core orchestration service for AI execution.

    This is the primary entry point for executing AI requests.

    Flow:
        validate
        ↓
        select provider
        ↓
        execute provider (with retries)
        ↓
        normalize response
        ↓
        return AIResponse

    Raises
    ------
    ValidationError
        If the request is invalid.
    ProviderSelectionError
        If provider selection fails.
    ProviderError
        If provider execution fails with a recoverable error.
    RetryExhaustedError
        If all retry attempts are exhausted.
    """

    def __init__(
        self,
        manager: AIManager,
        provider_selector: ProviderSelector,
        response_processor: ResponseProcessor,
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        """
        Initialize the orchestrator.

        Parameters
        ----------
        manager : AIManager
            The AI manager for execution.
        provider_selector : ProviderSelector
            The provider selector.
        response_processor : ResponseProcessor
            The response processor.
        retry_policy : RetryPolicy | None, optional
            Retry policy for execution. Defaults to default retry policy.
        """
        self._manager = manager
        self._provider_selector = provider_selector
        self._response_processor = response_processor
        self._retry_policy = retry_policy or RetryPolicy.default()

    @property
    def manager(self) -> AIManager:
        return self._manager

    @property
    def provider_selector(self) -> ProviderSelector:
        return self._provider_selector

    @property
    def response_processor(self) -> ResponseProcessor:
        return self._response_processor

    @property
    def retry_policy(self) -> RetryPolicy:
        return self._retry_policy

    # ------------------------------------------------------------------
    # Core Execution
    # ------------------------------------------------------------------

    def execute(
        self,
        request: AIRequest,
        plan: ExecutionPlan,
        context: Any = None,
    ) -> AIResponse:
        """
        Execute a request using the orchestrator.

        Parameters
        ----------
        request : AIRequest
            The request to execute.
        plan : ExecutionPlan
            The execution plan.
        context : Any, optional
            Execution context.

        Returns
        -------
        AIResponse
            The execution result.

        Raises
        ------
        ValidationError
            If the request is invalid.
        ProviderSelectionError
            If provider selection fails.
        ProviderError
            If provider execution fails.
        RetryExhaustedError
            If all retry attempts are exhausted.
        """
        # 1. Validate request
        self._validate_request(request)

        # 2. Select provider
        start_time = time.time()
        provider, model = self._provider_selector.select(
            request=request,
            preferred_provider=plan.provider,
            preferred_model=plan.model,
        )

        # 3. Execute with retries
        def _execute():
            if model:
                request.model = model
            return self._manager.execute(
                provider_name=provider.name,
                request=request,
                context=context,
            )

        try:
            response, attempt_count, total_time = self._retry_policy.execute(_execute)
        except RetryExhaustedError as e:
            # All retries failed — preserve the original error
            return self._response_processor.create_error_response(
                error=str(e),
                provider_name=provider.name,
                model_name=model,
            )
        except ProviderError as e:
            # Provider-specific error (e.g., API key, rate limit)
            return self._response_processor.create_error_response(
                error=str(e),
                provider_name=provider.name,
                model_name=model,
            )
        # Any other exception (e.g., programming error) re-raises

        # 4. Process response
        response = self._response_processor.process(
            raw_response=response,
            provider_name=provider.name,
            model_name=model,
            start_time=start_time,
        )

        # Add retry info to metadata
        response.metadata["retry_attempts"] = attempt_count
        response.metadata["total_time"] = total_time

        return response

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate_request(self, request: AIRequest) -> None:
        """
        Validate an AIRequest.

        Raises
        ------
        ValidationError
            If validation fails.
        """
        if not request.prompt and request.input is None:
            raise ValidationError(
                "Request must have either prompt or input."
            )

        if request.task == "chat" and not request.prompt:
            raise ValidationError(
                "Chat request must have a prompt."
            )

        if request.task == "generate" and request.input is None and not request.prompt:
            raise ValidationError(
                "Generate request must have input or prompt."
            )