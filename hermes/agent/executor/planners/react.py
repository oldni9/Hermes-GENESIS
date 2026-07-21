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

from hermes.ai.response import AIResponse
from hermes.agent.executor.engine import ExecutionEngine
from hermes.agent.executor.planners.base import Planner, PlannerState, PlannerConfig
from hermes.agent.executor.result import AgentResult
from hermes.agent.executor.trace import AgentTrace, TraceEventType


class ReActPlanner:
    """
    Standard ReAct planner. Executes turns until completion or max iterations.
    """
    def run(self, engine: ExecutionEngine, state: PlannerState, config: PlannerConfig) -> AgentResult:
        start_time = time.time()

        for iteration in range(state.iteration + 1, config.max_iterations + 1):
            state.iteration = iteration
            state.trace.add_event(iteration, TraceEventType.ITERATION_START)
            state.trace.add_event(iteration, TraceEventType.PLANNER_ITERATION)

            # 1. Execute Turn
            exec_response = engine.execute_turn(state.trace, iteration, config)

            if not exec_response.success:
                state.trace.add_event(iteration, TraceEventType.FAILED)
                state.trace.add_event(iteration, TraceEventType.ITERATION_FINISH)
                state.trace.finalize()
                return AgentResult(
                    response=exec_response,
                    iterations=iteration,
                    duration=time.time() - start_time,
                    token_usage={"prompt_tokens": state.trace.metrics.total_prompt_tokens, "completion_tokens": state.trace.metrics.total_completion_tokens},
                    stop_reason="pipeline_error",
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
                stop_reason="completed",
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
            stop_reason="max_iterations",
            trace=state.trace
        )