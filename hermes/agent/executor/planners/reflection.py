"""
===============================================================================
Reflection Planner
===============================================================================

Adds a self-critique loop. After execution, it asks a critic LLM to review
the answer. If rejected, it injects the critique and continues.
Stateless: tracks reflections via PlannerState.
===============================================================================
"""

from __future__ import annotations

import time

from hermes.ai.request import AIRequest
from hermes.ai.response import AIResponse
from hermes.core.errors import HermesRuntimeError, ExecutionCancelled, DeadlineExceeded, BudgetExceeded
from hermes.agent.executor.engine import ExecutionEngine
from hermes.agent.executor.planners.base import Planner, PlannerState, PlannerConfig
from hermes.agent.executor.protocols import PipelineProtocol
from hermes.agent.executor.result import AgentResult, StopReason
from hermes.agent.executor.trace import AgentTrace, TraceEventType


class ReflectionPlanner:
    """
    A planner that uses an LLM to critique the execution engine's output.
    Stateless; relies on PlannerState for iteration tracking.
    """
    def __init__(self, pipeline: PipelineProtocol, provider: str, model: str = ""):
        self._pipeline = pipeline
        self._provider = provider
        self._model = model

    def run(self, engine: ExecutionEngine, state: PlannerState, config: PlannerConfig) -> AgentResult:
        start_time = time.time()

        while state.reflection_count < config.max_reflections:
            state.iteration += 1
            if state.runtime_context:
                state.runtime_context.metrics.iterations = state.iteration
                state.runtime_context.metrics.planner_iterations = state.iteration

            state.trace.add_event(state.iteration, TraceEventType.ITERATION_START)
            state.trace.add_event(state.iteration, TraceEventType.PLANNER_ITERATION)

            # 1. Execute Turn directly via Engine
            try:
                exec_response = engine.execute_turn(state.trace, state.iteration, config)
            except HermesRuntimeError as e:
                stop_reason = StopReason.PIPELINE_ERROR
                if isinstance(e, ExecutionCancelled):
                    stop_reason = StopReason.CANCELLED
                elif isinstance(e, DeadlineExceeded):
                    stop_reason = StopReason.DEADLINE_EXCEEDED
                elif isinstance(e, BudgetExceeded):
                    stop_reason = StopReason.TOKEN_LIMIT
                    
                state.trace.add_event(state.iteration, TraceEventType.FAILED)
                state.trace.add_event(state.iteration, TraceEventType.ITERATION_FINISH)
                state.trace.finalize()
                
                final_response = AIResponse(
                    success=False,
                    message=str(e),
                    provider=self._provider,
                    model=self._model,
                )
                return AgentResult(
                    response=final_response,
                    iterations=state.iteration,
                    duration=time.time() - start_time,
                    token_usage={"prompt_tokens": state.trace.metrics.total_prompt_tokens, "completion_tokens": state.trace.metrics.total_completion_tokens},
                    stop_reason=stop_reason,
                    trace=state.trace
                )

            if not exec_response.success:
                state.trace.add_event(state.iteration, TraceEventType.FAILED)
                state.trace.add_event(state.iteration, TraceEventType.ITERATION_FINISH)
                state.trace.finalize()
                return AgentResult(
                    response=exec_response,
                    iterations=state.iteration,
                    duration=time.time() - start_time,
                    token_usage={"prompt_tokens": state.trace.metrics.total_prompt_tokens, "completion_tokens": state.trace.metrics.total_completion_tokens},
                    stop_reason=StopReason.PIPELINE_ERROR,
                    trace=state.trace
                )

            # 2. Ask Critic
            state.trace.add_event(state.iteration, TraceEventType.REFLECTION_START)
            critique_response = self._ask_critic(exec_response, config)
            
            approved = critique_response.text().strip().upper().startswith("APPROVED")
            
            state.reflection_count += 1
            state.trace.add_event(state.iteration, TraceEventType.REFLECTION_FINISH, {"approved": approved, "count": state.reflection_count})

            if approved:
                state.conversation.add_assistant(exec_response.text() or "")
                state.trace.add_event(state.iteration, TraceEventType.COMPLETED)
                state.trace.add_event(state.iteration, TraceEventType.ITERATION_FINISH)
                state.trace.finalize()
                return AgentResult(
                    response=exec_response,
                    iterations=state.iteration,
                    duration=time.time() - start_time,
                    token_usage={"prompt_tokens": state.trace.metrics.total_prompt_tokens, "completion_tokens": state.trace.metrics.total_completion_tokens},
                    stop_reason=StopReason.COMPLETED,
                    trace=state.trace
                )

            # 3. Inject Critique and Loop
            critique_text = critique_response.text()
            state.conversation.add_assistant(exec_response.text() or "")
            state.conversation.add_user(f"Critique: {critique_text}\n\nPlease revise your previous answer based on this critique.")
            state.trace.add_event(state.iteration, TraceEventType.PLANNER_DECISION, {"action": "continue"})
            state.trace.add_event(state.iteration, TraceEventType.ITERATION_FINISH)

        # Max reflections reached
        state.trace.add_event(state.iteration, TraceEventType.MAX_ITERATIONS_EXCEEDED)
        state.trace.add_event(state.iteration, TraceEventType.ITERATION_FINISH)
        state.trace.finalize()
        
        final_response = AIResponse(
            success=False,
            message=f"Agent reached maximum reflections ({config.max_reflections}) without approval.",
            provider=self._provider,
            model=self._model,
        )
        return AgentResult(
            response=final_response,
            iterations=state.iteration,
            duration=time.time() - start_time,
            token_usage={"prompt_tokens": state.trace.metrics.total_prompt_tokens, "completion_tokens": state.trace.metrics.total_completion_tokens},
            stop_reason=StopReason.MAX_REFLECTIONS,
            trace=state.trace
        )

    def _ask_critic(self, response: AIResponse, config: PlannerConfig) -> AIResponse:
        """Run a separate LLM call to critique the last answer."""
        answer = response.text()
        prompt_text = config.reflection_prompt.format(answer=answer)
        
        messages = [{"role": "user", "content": prompt_text}]
        request = AIRequest(
            prompt="",
            input=None,
            provider=self._provider,
            model=self._model,
            task="chat",
            options={"messages": messages},
            metadata={},
        )
        
        return self._pipeline.execute(
            provider=self._provider,
            request=request,
            context=None,
            use_cache=False,
        )

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture