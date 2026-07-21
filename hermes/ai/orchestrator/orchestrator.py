"""
===============================================================================
Hermes AI Orchestrator
===============================================================================
"""
from __future__ import annotations
import logging
import time
from typing import Any
from hermes.ai.manager import AIManager
from hermes.ai.request import AIRequest
from hermes.ai.response import AIResponse
from hermes.ai.tool import ToolManager as BaseToolManager, ToolResult, ToolStatus
from hermes.ai.adapters.provider_tool_adapter import ProviderToolAdapter
from hermes.core.exceptions import ProviderError
from hermes.ai.orchestrator.execution_plan import ExecutionPlan
from hermes.ai.orchestrator.provider_selector import ProviderSelector
from hermes.ai.orchestrator.retry_policy import RetryPolicy
from hermes.ai.orchestrator.response_processor import ResponseProcessor
from hermes.ai.orchestrator.exceptions import ValidationError, RetryExhaustedError

logger = logging.getLogger(__name__)

class AIOrchestrator:
    def __init__(self, manager: AIManager, provider_selector: ProviderSelector, response_processor: ResponseProcessor, retry_policy: RetryPolicy | None = None, tool_manager: BaseToolManager | None = None) -> None:
        self._manager = manager
        self._provider_selector = provider_selector
        self._response_processor = response_processor
        self._retry_policy = retry_policy or RetryPolicy.default()
        self._tool_manager = tool_manager

    @property
    def tool_manager(self) -> BaseToolManager | None: return self._tool_manager

    def execute(self, request: AIRequest, plan: ExecutionPlan, context: Any = None) -> AIResponse:
        self._validate_request(request)
        start_time = time.time()
        provider, model = self._provider_selector.select(request=request, preferred_provider=plan.provider, preferred_model=plan.model)

        def _execute():
            if model: request.model = model
            return self._manager.execute(provider_name=provider.name, request=request, context=context)

        try:
            response, attempt_count, total_time = self._retry_policy.execute(_execute)
        except RetryExhaustedError as e:
            return self._response_processor.create_error_response(error=str(e), provider_name=provider.name, model_name=model)
        except ProviderError as e:
            return self._response_processor.create_error_response(error=str(e), provider_name=provider.name, model_name=model)

        response = self._response_processor.process(raw_response=response, provider_name=provider.name, model_name=model, start_time=start_time)
        response.metadata["retry_attempts"] = attempt_count
        response.metadata["total_time"] = total_time

        if self._tool_manager is not None and response.tool_calls:
            response.metadata = response.metadata or {}
            converted_calls, conversion_errors = ProviderToolAdapter.convert_provider_tool_calls(response.tool_calls)
            execution_results = self._tool_manager.execute_batch(converted_calls, context=context) if converted_calls else []
            
            results_by_id = {r.call_id: r for r in execution_results}
            all_results = []
            for tc in response.tool_calls:
                if tc.id in results_by_id: all_results.append(results_by_id[tc.id])
                else:
                    error = next((e for e in conversion_errors if e.call_id == tc.id), None)
                    all_results.append(error if error else ToolResult(call_id=tc.id, status=ToolStatus.FAILED, error="Unknown error"))
            response.metadata["tool_results"] = all_results

        return response

    def _validate_request(self, request: AIRequest) -> None:
        if not request.prompt and request.input is None: raise ValidationError("Request must have either prompt or input.")
        if request.task == "chat" and not request.prompt: raise ValidationError("Chat request must have a prompt.")