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
    - Tool execution (Sprint 4)

NO streaming.
NO tool loop.
NO batch execution.
NO cache logic (cache lives in pipeline).
===============================================================================
"""

from __future__ import annotations

import logging
import time
from typing import Any

from hermes.ai.manager import AIManager
from hermes.ai.request import AIRequest
from hermes.ai.response import AIResponse
from hermes.ai.tool import ToolManager, ToolResult, ToolStatus
from hermes.ai.adapters.provider_tool_adapter import ProviderToolAdapter
from hermes.core.exceptions import ProviderError

from hermes.ai.orchestrator.execution_plan import ExecutionPlan
from hermes.ai.orchestrator.provider_selector import ProviderSelector
from hermes.ai.orchestrator.retry_policy import RetryPolicy
from hermes.ai.orchestrator.response_processor import ResponseProcessor
from hermes.ai.orchestrator.exceptions import (
    ValidationError,
    RetryExhaustedError,
)

logger = logging.getLogger(__name__)


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
        execute tools (if any)
        ↓
        return AIResponse
    """

    def __init__(
        self,
        manager: AIManager,
        provider_selector: ProviderSelector,
        response_processor: ResponseProcessor,
        retry_policy: RetryPolicy | None = None,
        tool_manager: ToolManager | None = None,
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
        tool_manager : ToolManager | None, optional
            Tool manager for executing tool calls. If None, tools are not executed.
        """
        self._manager = manager
        self._provider_selector = provider_selector
        self._response_processor = response_processor
        self._retry_policy = retry_policy or RetryPolicy.default()
        self._tool_manager = tool_manager

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

    @property
    def tool_manager(self) -> ToolManager | None:
        return self._tool_manager

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
            # All retries failed – preserve the original error
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

        # 5. Execute tools if any (single-pass, no agent loop)
        if self._tool_manager is not None and response.tool_calls:
            response.metadata = response.metadata or {}
            logger.debug("Converting %d tool calls", len(response.tool_calls))

            converted_calls, conversion_errors = ProviderToolAdapter.convert_provider_tool_calls(
                response.tool_calls
            )

            if conversion_errors:
                for err in conversion_errors:
                    logger.debug("Conversion failed for call %s: %s", err.call_id, err.error)

            # Execute successfully converted calls
            if converted_calls:
                execution_results = self._tool_manager.execute_batch(converted_calls, context=context)
            else:
                execution_results = []

            # Merge results in original order by call_id
            results_by_id = {r.call_id: r for r in execution_results}
            all_results = []
            for tc in response.tool_calls:
                if tc.id in results_by_id:
                    all_results.append(results_by_id[tc.id])
                else:
                    error = next((e for e in conversion_errors if e.call_id == tc.id), None)
                    if error:
                        all_results.append(error)
                    else:
                        # Fallback (should not happen)
                        all_results.append(ToolResult(
                            call_id=tc.id,
                            status=ToolStatus.FAILED,
                            error="Unknown error",
                        ))
            response.metadata["tool_results"] = all_results
            logger.debug("Tool execution completed for %d calls", len(all_results))

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