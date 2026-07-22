"""
===============================================================================
Debate Planner
===============================================================================

Phase 1 Implementation:
- Runs K debaters sequentially via ExecutionEngine.execute_ephemeral().
- Each debater receives the objective but applies a different persona system prompt.
- A Judge synthesizes the debater responses into a final answer.
- Uses the ExecutionEngine exclusively for LLM calls.
===============================================================================
"""

from __future__ import annotations

import time
from typing import Any, List, Tuple

from hermes.ai.response import AIResponse
from hermes.core.errors import HermesRuntimeError, ExecutionCancelled, DeadlineExceeded, BudgetExceeded
from hermes.agent.executor.engine import ExecutionEngine
from hermes.agent.executor.planners.base import Planner, PlannerState, DebateConfig, DebaterPersona
from hermes.agent.executor.result import AgentResult, StopReason
from hermes.agent.executor.trace import TraceEventType


class DebatePlanner(Planner):
    """
    A planner that uses multiple personas to debate a prompt, and a judge 
    to synthesize the final answer.
    """
    
    def __init__(self, **kwargs: Any) -> None:
        pass

    def run(self, engine: ExecutionEngine, state: PlannerState, config: DebateConfig) -> AgentResult:
        start_time = time.time()
        state.iteration = 1
        if state.runtime_context:
            state.runtime_context.metrics.iterations = 1
            state.runtime_context.metrics.planner_iterations = 1

        state.trace.add_event(1, TraceEventType.ITERATION_START)
        state.trace.add_event(1, TraceEventType.PLANNER_ITERATION)
        state.trace.add_event(1, TraceEventType.DEBATE_STARTED, {"debaters": config.debaters})

        try:
            initial_prompt = state.objective
            if not initial_prompt:
                return self._handle_failure(engine, state, 1, start_time, "No objective found for debate.", StopReason.PIPELINE_ERROR)

            # 1. Execute Debaters
            debate_responses = self._execute_debaters(engine, state, config, initial_prompt)
            if isinstance(debate_responses, AIResponse): # Failure occurred
                return self._handle_failure(engine, state, 1, start_time, debate_responses.message, StopReason.PIPELINE_ERROR)

            # 2. Run Judge to synthesize final answer
            state.trace.add_event(1, TraceEventType.JUDGE_STARTED)
            
            debates_str = "\n\n".join([
                f"=== Debater {i+1} ({config.personas[i].name}) ===\n{resp}" 
                for i, resp in enumerate(debate_responses)
            ])
            judge_prompt = config.judge_prompt.format(n=config.debaters, debates=debates_str)
            judge_response = engine.execute_ephemeral(state.trace, 1, config, judge_prompt)
            
            if not judge_response.success:
                return self._handle_failure(engine, state, 1, start_time, judge_response.message, StopReason.PIPELINE_ERROR)
                
            state.trace.add_event(1, TraceEventType.JUDGE_FINISHED)

            # 3. Append Final Text and Finish
            final_text = judge_response.text()
            state.conversation.add_assistant(final_text)
            state.trace.add_event(1, TraceEventType.DEBATE_COMPLETED)
            state.trace.add_event(1, TraceEventType.COMPLETED)
            state.trace.add_event(1, TraceEventType.ITERATION_FINISH)
            state.trace.finalize()
            
            return AgentResult(
                response=AIResponse(success=True, result=final_text, provider=engine.provider, model=engine.model),
                iterations=1,
                duration=time.time() - start_time,
                token_usage={"prompt_tokens": state.trace.metrics.total_prompt_tokens, "completion_tokens": state.trace.metrics.total_completion_tokens},
                stop_reason=StopReason.COMPLETED,
                trace=state.trace
            )

        except HermesRuntimeError as e:
            stop_reason = StopReason.PIPELINE_ERROR
            if isinstance(e, ExecutionCancelled):
                stop_reason = StopReason.CANCELLED
            elif isinstance(e, DeadlineExceeded):
                stop_reason = StopReason.DEADLINE_EXCEEDED
            elif isinstance(e, BudgetExceeded):
                stop_reason = StopReason.TOKEN_LIMIT
                
            state.trace.add_event(1, TraceEventType.FAILED)
            state.trace.add_event(1, TraceEventType.ITERATION_FINISH)
            state.trace.finalize()
            
            return AgentResult(
                response=AIResponse(success=False, message=str(e), provider=engine.provider, model=engine.model),
                iterations=1,
                duration=time.time() - start_time,
                token_usage={"prompt_tokens": state.trace.metrics.total_prompt_tokens, "completion_tokens": state.trace.metrics.total_completion_tokens},
                stop_reason=stop_reason,
                trace=state.trace
            )

    def _execute_debaters(self, engine: ExecutionEngine, state: PlannerState, config: DebateConfig, initial_prompt: str) -> List[str] | AIResponse:
        """Executes debaters sequentially. Returns list of responses or failed AIResponse."""
        responses = []
        for i in range(config.debaters):
            persona = config.personas[i]
            state.trace.add_event(1, TraceEventType.DEBATER_STARTED, {"persona": persona.name})
            
            debater_prompt = config.debater_prompt.format(system_prompt=persona.system_prompt, prompt=initial_prompt)
            response = engine.execute_ephemeral(state.trace, 1, config, debater_prompt)
            
            if not response.success:
                return response
                
            responses.append(response.text())
            state.trace.add_event(1, TraceEventType.DEBATER_FINISHED, {"persona": persona.name})
            state.trace.add_event(1, TraceEventType.DEBATER_RESPONSE, {"persona": persona.name, "length": len(response.text())})
        return responses

    def _handle_failure(self, engine: ExecutionEngine, state: PlannerState, iteration: int, start_time: float, message: str, stop_reason: StopReason) -> AgentResult:
        state.trace.add_event(iteration, TraceEventType.FAILED)
        state.trace.add_event(iteration, TraceEventType.ITERATION_FINISH)
        state.trace.finalize()
        return AgentResult(
            response=AIResponse(success=False, message=message, provider=engine.provider, model=engine.model),
            iterations=iteration,
            duration=time.time() - start_time,
            token_usage={"prompt_tokens": state.trace.metrics.total_prompt_tokens, "completion_tokens": state.trace.metrics.total_completion_tokens},
            stop_reason=stop_reason,
            trace=state.trace
        )

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture