"""
===============================================================================
Tree of Thought (ToT) Planner
===============================================================================

Phase 1 Implementation:
- Generates K candidate thoughts per step via ExecutionEngine.
- Evaluates and scores each candidate via ExecutionEngine.
- Selects the highest-scoring candidate to continue.
- Halts if a "FINAL ANSWER:" is generated or max_depth is reached.

Sprint 10.1 Fix:
- Uses an internal `path_history` list to maintain branch continuity 
  without polluting the user's conversation history.
- Handles markdown bullet list parsing.
- Uses engine properties for failure responses.
===============================================================================
"""

from __future__ import annotations

import ast
import json
import re
import time
from typing import Any, List, Tuple

from hermes.ai.response import AIResponse
from hermes.core.errors import HermesRuntimeError, ExecutionCancelled, DeadlineExceeded, BudgetExceeded
from hermes.agent.executor.engine import ExecutionEngine
from hermes.agent.executor.planners.base import Planner, PlannerState, TreeOfThoughtConfig
from hermes.agent.executor.result import AgentResult, StopReason
from hermes.agent.executor.trace import TraceEventType


class StructuredListParser:
    """Reusable parser for extracting lists from LLM output."""
    
    @staticmethod
    def parse(text: str) -> List[Any]:
        # 1. Try JSON
        try:
            start = text.find('[')
            end = text.rfind(']') + 1
            if start != -1 and end != -1:
                data = json.loads(text[start:end])
                if isinstance(data, list):
                    return data
        except Exception:
            pass
        
        # 2. Try Python literal (e.g., ['a', 'b'])
        try:
            start = text.find('[')
            end = text.rfind(']') + 1
            if start != -1 and end != -1:
                val = ast.literal_eval(text[start:end])
                if isinstance(val, list):
                    return val
        except Exception:
            pass
            
        # 3. Try numbered list (e.g., "1. Thought one\n2. Thought two")
        items = re.findall(r'(?:^|\n)\d+\.\s*(.*?)(?=\n\d+\.|$)', text, re.DOTALL)
        if items:
            return [item.strip().strip('"').strip("'") for item in items]
            
        # 4. Try markdown bullets (e.g., "- Thought A\n* Thought B\n• Thought C")
        items = re.findall(r'(?:^|\n)[-\*•]\s*(.*?)(?=\n[-\*•]|$)', text, re.DOTALL)
        if items:
            return [item.strip().strip('"').strip("'") for item in items]
            
        return []


class TreeOfThoughtPlanner(Planner):
    """
    A planner that explores multiple reasoning branches (thoughts) at each step,
    evaluates them, and selects the most promising one to continue.
    Uses the ExecutionEngine exclusively for LLM calls.
    """
    
    def __init__(self, **kwargs: Any) -> None:
        # ExecutionEngine provides all runtime dependencies.
        # Planner intentionally stores no provider/model state.
        pass

    def run(self, engine: ExecutionEngine, state: PlannerState, config: TreeOfThoughtConfig) -> AgentResult:
        start_time = time.time()
        depth = 0
        path_history: List[str] = []
        
        while depth < config.max_depth:
            depth += 1
            state.iteration = depth
            if state.runtime_context:
                state.runtime_context.metrics.iterations = depth
                state.runtime_context.metrics.planner_iterations = depth

            state.trace.add_event(depth, TraceEventType.ITERATION_START)
            state.trace.add_event(depth, TraceEventType.PLANNER_ITERATION)

            try:
                # 1. Generate K candidates via Engine (Ephemeral)
                context_str = " -> ".join(path_history) if path_history else "None"
                gen_prompt = f"Path so far: {context_str}\n\n" + config.generator_prompt.format(k=config.branch_factor)
                gen_response = engine.execute_ephemeral(state.trace, depth, config, gen_prompt)
                
                if not gen_response.success:
                    return self._handle_failure(engine, state, depth, start_time, gen_response.message, StopReason.PIPELINE_ERROR)

                candidates = StructuredListParser.parse(gen_response.text())
                
                # Build branch metadata
                branches = [{"id": f"b{depth}_{i}", "thought": c} for i, c in enumerate(candidates)]
                state.trace.add_event(depth, TraceEventType.TOT_BRANCH_GENERATED, {
                    "depth": depth,
                    "count": len(branches),
                    "branches": branches
                })
                
                # Edge case: zero branches generated
                if not candidates:
                    state.trace.add_event(depth, TraceEventType.TOT_SEARCH_FINISHED, {"reason": "no_candidates"})
                    state.trace.add_event(depth, TraceEventType.ITERATION_FINISH)
                    state.trace.finalize()
                    return AgentResult(
                        response=AIResponse(success=False, message="ToT generated 0 candidates.", provider=engine.provider, model=engine.model),
                        iterations=depth,
                        duration=time.time() - start_time,
                        stop_reason=StopReason.PIPELINE_ERROR,
                        trace=state.trace
                    )

                # 2. Evaluate candidates via Engine (Ephemeral)
                thoughts_str = "\n".join([f"{i+1}. {c}" for i, c in enumerate(candidates)])
                eval_prompt = config.evaluator_prompt.format(thoughts=thoughts_str)
                eval_response = engine.execute_ephemeral(state.trace, depth, config, eval_prompt)
                
                if not eval_response.success:
                    return self._handle_failure(engine, state, depth, start_time, eval_response.message, StopReason.PIPELINE_ERROR)

                scores = StructuredListParser.parse(eval_response.text())
                state.trace.add_event(depth, TraceEventType.TOT_BRANCH_EVALUATED, {
                    "depth": depth,
                    "scores": scores
                })
                
                # 3. Select best candidate
                best_idx, best_thought = self._select_best(candidates, scores)
                best_branch_id = f"b{depth}_{best_idx}"
                state.trace.add_event(depth, TraceEventType.TOT_BRANCH_SELECTED, {
                    "depth": depth,
                    "branch_id": best_branch_id,
                    "thought": best_thought, 
                    "index": best_idx
                })

                # 4. Check for final answer
                if "FINAL ANSWER:" in best_thought:
                    final_text = best_thought.replace("FINAL ANSWER:", "").strip()
                    state.conversation.add_assistant(final_text)
                    state.trace.add_event(depth, TraceEventType.COMPLETED)
                    state.trace.add_event(depth, TraceEventType.TOT_SEARCH_FINISHED, {"reason": "final_answer"})
                    state.trace.add_event(depth, TraceEventType.ITERATION_FINISH)
                    state.trace.finalize()
                    
                    final_response = AIResponse(success=True, result=final_text, provider=engine.provider, model=engine.model)
                    return AgentResult(
                        response=final_response,
                        iterations=depth,
                        duration=time.time() - start_time,
                        token_usage={"prompt_tokens": state.trace.metrics.total_prompt_tokens, "completion_tokens": state.trace.metrics.total_completion_tokens},
                        stop_reason=StopReason.COMPLETED,
                        trace=state.trace
                    )

                # 5. Update internal path history and continue
                path_history.append(best_thought)
                state.trace.add_event(depth, TraceEventType.ITERATION_FINISH)

            except HermesRuntimeError as e:
                stop_reason = StopReason.PIPELINE_ERROR
                if isinstance(e, DeadlineExceeded):
                    stop_reason = StopReason.DEADLINE_EXCEEDED
                elif isinstance(e, BudgetExceeded):
                    stop_reason = StopReason.TOKEN_LIMIT
                elif isinstance(e, ExecutionCancelled):
                    stop_reason = StopReason.CANCELLED
                    
                state.trace.add_event(depth, TraceEventType.FAILED)
                state.trace.add_event(depth, TraceEventType.TOT_SEARCH_FINISHED, {"reason": "runtime_error"})
                state.trace.add_event(depth, TraceEventType.ITERATION_FINISH)
                state.trace.finalize()
                
                return AgentResult(
                    response=AIResponse(success=False, message=str(e), provider=engine.provider, model=engine.model),
                    iterations=depth,
                    duration=time.time() - start_time,
                    token_usage={"prompt_tokens": state.trace.metrics.total_prompt_tokens, "completion_tokens": state.trace.metrics.total_completion_tokens},
                    stop_reason=stop_reason,
                    trace=state.trace
                )

        # Max depth reached
        state.trace.add_event(depth, TraceEventType.MAX_ITERATIONS_EXCEEDED)
        state.trace.add_event(depth, TraceEventType.TOT_SEARCH_FINISHED, {"reason": "max_depth"})
        state.trace.add_event(depth, TraceEventType.ITERATION_FINISH)
        state.trace.finalize()
        
        return AgentResult(
            response=AIResponse(success=False, message=f"ToT reached max depth ({config.max_depth}) without final answer.", provider=engine.provider, model=engine.model),
            iterations=depth,
            duration=time.time() - start_time,
            token_usage={"prompt_tokens": state.trace.metrics.total_prompt_tokens, "completion_tokens": state.trace.metrics.total_completion_tokens},
            stop_reason=StopReason.MAX_ITERATIONS,
            trace=state.trace
        )

    def _select_best(self, candidates: List[str], scores: List[int]) -> Tuple[int, str]:
        if not scores or len(scores) != len(candidates) or not isinstance(scores[0], (int, float)):
            # Fallback: pick first candidate if evaluation parsing failed or invalid
            return 0, candidates[0]
            
        best_idx = scores.index(max(scores))
        return best_idx, candidates[best_idx]

    def _handle_failure(self, engine: ExecutionEngine, state: PlannerState, depth: int, start_time: float, message: str, stop_reason: StopReason) -> AgentResult:
        state.trace.add_event(depth, TraceEventType.FAILED)
        state.trace.add_event(depth, TraceEventType.TOT_SEARCH_FINISHED, {"reason": "engine_failure"})
        state.trace.add_event(depth, TraceEventType.ITERATION_FINISH)
        state.trace.finalize()
        return AgentResult(
            response=AIResponse(success=False, message=message, provider=engine.provider, model=engine.model),
            iterations=depth,
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