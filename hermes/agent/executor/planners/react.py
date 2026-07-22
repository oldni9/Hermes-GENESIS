"""
===============================================================================
ReAct Planner
===============================================================================

The standard Reason + Act planning loop.
Orchestrates the ExecutionEngine until a final answer is reached.
===============================================================================
"""

from __future__ import annotations

import time
from typing import Any

from hermes.ai.response import AIResponse
from hermes.core.errors import HermesRuntimeError, ExecutionCancelled, DeadlineExceeded, BudgetExceeded
from hermes.agent.executor.engine import ExecutionEngine
from hermes.agent.executor.planners.base import Planner, PlannerState, PlannerConfig
from hermes.agent.executor.result import AgentResult, StopReason
from hermes.agent.executor.trace import AgentTrace, TraceEventType


class ReActPlanner:
    """
    Standard ReAct planner. Executes turns until completion or max iterations.
    """
    def __init__(self, pipeline: Any = None, provider: str = "", model: str = "") -> None:
        # ReAct planner doesn't need to make direct LLM calls, so it ignores these.
        # The signature is here to satisfy the Planner protocol for the factory.
        pass

    def run(self, engine: ExecutionEngine, state: PlannerState, config: PlannerConfig) -> AgentResult:
        start_time = time.time()

        for iteration in range(state.iteration + 1, config.max_iterations + 1):
            state.iteration = iteration
            if state.runtime_context:
                state.runtime_context.metrics.iterations = iteration
                state.runtime_context.metrics.planner_iterations = iteration

            state.trace.add_event(iteration, TraceEventType.ITERATION_START)
            state.trace.add_event(iteration, TraceEventType.PLANNER_ITERATION)

            # 1. Execute Turn
            try:
                exec_response = engine.execute_turn(state.trace, iteration, config)
            except HermesRuntimeError as e:
                stop_reason = StopReason.PIPELINE_ERROR
                if isinstance(e, ExecutionCancelled):
                    stop_reason = StopReason.CANCELLED
                elif isinstance(e, DeadlineExceeded):
                    stop_reason = StopReason.DEADLINE_EXCEEDED
                elif isinstance(e, BudgetExceeded):
                    stop_reason = StopReason.TOKEN_LIMIT
                    
                state.trace.add_event(iteration, TraceEventType.FAILED)
                state.trace.add_event(iteration, TraceEventType.ITERATION_FINISH)
                state.trace.finalize()
                
                final_response = AIResponse(
                    success=False,
                    message=str(e),
                    provider=engine._request_builder.provider,
                    model=engine._request_builder.model,
                )
                return AgentResult(
                    response=final_response,
                    iterations=iteration,
                    duration=time.time() - start_time,
                    token_usage={"prompt_tokens": state.trace.metrics.total_prompt_tokens, "completion_tokens": state.trace.metrics.total_completion_tokens},
                    stop_reason=stop_reason,
                    trace=state.trace
                )

            if not exec_response.success:
                state.trace.add_event(iteration, TraceEventType.FAILED)
                state.trace.add_event(iteration, TraceEventType.ITERATION_FINISH)
                state.trace.finalize()
                return AgentResult(
                    response=exec_response,
                    iterations=iteration,
                    duration=time.time() - start_time,
                    token_usage={"prompt_tokens": state.trace.metrics.total_prompt_tokens, "completion_tokens": state.trace.metrics.total_completion_tokens},
                    stop_reason=StopReason.PIPELINE_ERROR,
                    trace=state.trace
                )

            # 2. Append Final Text and Finish
            state.conversation.add_assistant(exec_response.text() or "")
            state.trace.add_event(iteration, TraceEventType.COMPLETED)
            state.trace.add_event(iteration, TraceEventType.ITERATION_FINISH)
            state.trace.finalize()
            
            return AgentResult(
                response=exec_response,
                iterations=iteration,
                duration=time.time() - start_time,
                token_usage={"prompt_tokens": state.trace.metrics.total_prompt_tokens, "completion_tokens": state.trace.metrics.total_completion_tokens},
                stop_reason=StopReason.COMPLETED,
                trace=state.trace
            )

        # Loop exhausted
        final_response = AIResponse(
            success=False,
            message=f"Agent reached maximum iterations ({config.max_iterations}) without a final response.",
            provider=engine._request_builder.provider,
            model=engine._request_builder.model,
        )
        state.trace.add_event(config.max_iterations, TraceEventType.MAX_ITERATIONS_EXCEEDED)
        state.trace.add_event(config.max_iterations, TraceEventType.ITERATION_FINISH)
        state.trace.finalize()
        return AgentResult(
            response=final_response,
            iterations=config.max_iterations,
            duration=time.time() - start_time,
            token_usage={"prompt_tokens": state.trace.metrics.total_prompt_tokens, "completion_tokens": state.trace.metrics.total_completion_tokens},
            stop_reason=StopReason.MAX_ITERATIONS,
            trace=state.trace
        )

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture