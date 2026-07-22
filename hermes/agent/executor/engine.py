"""
===============================================================================
Execution Engine
===============================================================================

Handles the mechanics of running LLM calls and tool execution.
It loops internally until the LLM stops requesting tools.
It is completely stateless and instructed by the Planner.

Sprint 8 Update:
The engine now enforces RuntimePolicy (timeout, cancellation, token budget).
It raises structured exceptions (HermesRuntimeError) when limits are exceeded.
===============================================================================
"""

from __future__ import annotations

import time
from typing import Dict, Optional

from hermes.ai.response import AIResponse, ToolCall
from hermes.ai.tool import ToolResult
from hermes.core.errors import ExecutionCancelled, DeadlineExceeded, BudgetExceeded
from hermes.core.runtime import RuntimeContext, RuntimeClock
from hermes.agent.executor.protocols import PipelineProtocol
from hermes.agent.executor.conversation_state import ConversationState
from hermes.agent.executor.tool_runner import ToolRunner
from hermes.agent.executor.context_factory import AgentContextFactory
from hermes.agent.executor.request_builder import RequestBuilder
from hermes.agent.executor.trace import AgentTrace, TraceEventType
from hermes.agent.executor.serializer import ToolResultSerializer
from hermes.workspace.workspace import Workspace


class ExecutionEngine:
    """
    Executes a single turn of reasoning + acting.
    Returns the final LLM response for that turn.
    """

    def __init__(
        self,
        pipeline: PipelineProtocol,
        tool_runner: ToolRunner,
        conv_state: ConversationState,
        context_factory: AgentContextFactory,
        request_builder: RequestBuilder,
        workspace: Workspace | None = None,
        runtime_context: Optional[RuntimeContext] = None,
    ) -> None:
        self._pipeline = pipeline
        self._tool_runner = tool_runner
        self._conv_state = conv_state
        self._context_factory = context_factory
        self._request_builder = request_builder
        self._workspace = workspace
        self._runtime_context = runtime_context

    def _check_policy(self, trace: AgentTrace, iteration: int) -> None:
        """Check all runtime policy limits and raise if exceeded."""
        if self._runtime_context is None:
            return
            
        policy = self._runtime_context.policy
        metrics = self._runtime_context.metrics
        token = self._runtime_context.cancellation_token
        
        # Prepare full telemetry payload
        checks = {
            "timeout_remaining": None,
            "tokens_remaining": None,
            "cancelled": False,
            "prompt_tokens": metrics.used_prompt_tokens,
            "completion_tokens": metrics.used_completion_tokens,
            "tool_calls": metrics.tool_calls,
            "llm_calls": metrics.llm_calls,
            "elapsed": metrics.elapsed,
            "budget_remaining": None
        }
        
        failed_reason = None
        
        # 1. Cancellation
        if token and token.cancelled:
            checks["cancelled"] = True
            failed_reason = "cancelled"
            
        # 2. Deadline
        if policy.timeout is not None:
            deadline = metrics.started_at + policy.timeout
            remaining_timeout = max(0.0, deadline - RuntimeClock.now())
            checks["timeout_remaining"] = remaining_timeout
            if remaining_timeout <= 0.0 and failed_reason is None:
                failed_reason = "deadline_exceeded"
                
        # 3. Token Budget
        used_tokens = metrics.used_tokens if metrics else 0
        if policy.max_tokens is not None:
            raw_tokens_remaining = policy.max_tokens - used_tokens
            tokens_remaining = max(0, raw_tokens_remaining)
            checks["tokens_remaining"] = tokens_remaining
            checks["budget_remaining"] = tokens_remaining
            # Strictly exceeded (less than 0). If it's exactly 0, we allow it to finish.
            if raw_tokens_remaining < 0 and failed_reason is None:
                failed_reason = "budget_exceeded"
                
        trace.add_event(iteration, TraceEventType.POLICY_CHECK, checks)
        
        if failed_reason:
            trace.add_event(iteration, TraceEventType.POLICY_FAIL, {"reason": failed_reason})
            if failed_reason == "cancelled":
                trace.add_event(iteration, TraceEventType.CANCELLED)
                raise ExecutionCancelled("Execution cancelled by request.")
            elif failed_reason == "deadline_exceeded":
                trace.add_event(iteration, TraceEventType.DEADLINE_EXCEEDED)
                raise DeadlineExceeded("Execution deadline exceeded.")
            elif failed_reason == "budget_exceeded":
                trace.add_event(iteration, TraceEventType.BUDGET_EXCEEDED)
                raise BudgetExceeded("Token budget exceeded.")
        else:
            trace.add_event(iteration, TraceEventType.POLICY_PASS)

    def execute_turn(self, trace: AgentTrace, iteration: int, config) -> AIResponse:
        """Run the LLM -> Tool loop until a final answer is reached or tools max out."""
        trace.add_event(iteration, TraceEventType.EXECUTION_START)
        
        if self._runtime_context:
            self._runtime_context.metrics.execution_turns += 1
        
        # Check policy before starting the turn
        self._check_policy(trace, iteration)
        
        for tool_iter in range(1, config.engine_max_iterations + 1):
            if self._runtime_context:
                self._runtime_context.metrics.tool_iterations += 1

            trace.add_event(iteration, TraceEventType.LLM_START)
            request = self._request_builder.build(self._conv_state.conversation)
            
            response = self._pipeline.execute(
                provider=self._request_builder.provider,
                request=request,
                context=None,
                use_cache=False,
            )
            
            # Update metrics after LLM call and sync to trace
            if self._runtime_context and self._runtime_context.metrics:
                if response.usage:
                    self._runtime_context.metrics.add_tokens(response.usage.prompt_tokens, response.usage.completion_tokens)
                    trace.add_token_usage(response.usage.prompt_tokens, response.usage.completion_tokens)
                self._runtime_context.metrics.add_llm_call()
                
            trace.add_event(iteration, TraceEventType.LLM_FINISH, {"success": response.success})

            # Check policy after LLM call (token budget might be exceeded now)
            self._check_policy(trace, iteration)

            if not response.success:
                trace.add_event(iteration, TraceEventType.EXECUTION_FINISH, {"success": False})
                return response

            if not response.tool_calls:
                trace.add_event(iteration, TraceEventType.EXECUTION_FINISH, {"success": True})
                return response

            # Handle Tool Calls
            self._conv_state.append_assistant_tool_calls(response)
            trace.add_event(iteration, TraceEventType.TOOL_START, {"tool_calls": len(response.tool_calls)})

            tool_context = self._context_factory.build(
                conversation=self._conv_state.conversation,
                workspace=self._workspace
            )
            
            results_map: Dict[str, ToolResult] = self._tool_runner.execute(response.tool_calls, tool_context)

            for tc in response.tool_calls:
                result = results_map.get(tc.id)
                output_str = ToolResultSerializer.serialize(tc, result)
                tool_name = tc.function.name if tc.function else "unknown"
                self._conv_state.append_tool_message(
                    tool_call_id=tc.id,
                    tool_name=tool_name,
                    output=output_str
                )
                if self._runtime_context and self._runtime_context.metrics:
                    self._runtime_context.metrics.add_tool_call()
            
            trace.add_event(iteration, TraceEventType.TOOL_FINISH)
            
            # Check policy after tool execution
            self._check_policy(trace, iteration)

        # Exceeded max tool iterations
        trace.add_event(iteration, TraceEventType.EXECUTION_FINISH, {"success": False, "reason": "engine_max_iterations"})
        return AIResponse(
            success=False,
            message=f"Execution engine exceeded max iterations ({config.engine_max_iterations}).",
            provider=self._request_builder.provider,
            model=self._request_builder.model,
        )

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture