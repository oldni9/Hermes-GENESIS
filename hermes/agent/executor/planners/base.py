"""
===============================================================================
Planner Base Architecture
===============================================================================

Separates planning strategy (Planner) from execution mechanics (ExecutionEngine).
Planners own the orchestration loop and instruct the engine to execute turns.
===============================================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

from hermes.ai.conversation import AIConversation
from hermes.core.runtime import RuntimeContext
from hermes.agent.executor.engine import ExecutionEngine
from hermes.agent.executor.result import AgentResult, StopReason
from hermes.agent.executor.trace import AgentTrace


@dataclass
class PlannerState:
    """Mutable state passed between planner iterations."""
    conversation: AIConversation
    trace: AgentTrace
    iteration: int = 0
    reflection_count: int = 0
    
    # Sprint 8 Addition
    runtime_context: Optional[RuntimeContext] = None


@dataclass
class PlannerConfig:
    """Configuration for planners and the execution engine."""
    planner_name: str = "react"  # Default planner name
    max_iterations: int = 10
    engine_max_iterations: int = 10
    max_reflections: int = 2
    reflection_prompt: str = "You are a critic. Review the following answer. If it is correct and complete, respond with 'APPROVED'. If not, respond with 'REJECT: [your critique]'.\n\nAnswer: {answer}"


@dataclass
class TreeOfThoughtConfig(PlannerConfig):
    """Configuration specific to the Tree of Thought planner."""
    planner_name: str = "tot"
    branch_factor: int = 3
    max_depth: int = 3
    evaluator_prompt: str = (
        "You are an evaluator. Given the conversation history and a list of proposed thoughts, "
        "score each thought from 1 to 10 based on its likelihood of leading to the correct final answer. "
        "Return ONLY a Python list of integers corresponding to the scores. "
        "Example format: [8, 5, 9]\n\nThoughts:\n{thoughts}"
    )
    generator_prompt: str = (
        "You are a reasoning agent. Given the conversation history, generate {k} distinct next thoughts or steps. "
        "If you have arrived at the final answer, prefix the thought with 'FINAL ANSWER:'. "
        "Return ONLY a Python list of strings. "
        "Example format: ['First thought', 'Second thought', 'FINAL ANSWER: The answer is 42']\n\n"
    )


class Planner(ABC):
    """
    Abstract Base Class for all planners.
    Planners own the orchestration loop and return the final result.
    """
    @abstractmethod
    def run(
        self, 
        engine: ExecutionEngine, 
        state: PlannerState, 
        config: PlannerConfig
    ) -> AgentResult:
        ...

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture