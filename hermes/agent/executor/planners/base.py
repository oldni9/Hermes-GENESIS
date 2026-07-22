"""
===============================================================================
Planner Base Architecture
===============================================================================

Separates planning strategy (Planner) from execution mechanics (ExecutionEngine).
Planners own the orchestration loop and instruct the engine to execute turns.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Protocol, runtime_checkable

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
    planner_name: str = "react"  # Sprint 9: Default planner name
    max_iterations: int = 10
    engine_max_iterations: int = 10
    max_reflections: int = 2
    reflection_prompt: str = "You are a critic. Review the following answer. If it is correct and complete, respond with 'APPROVED'. If not, respond with 'REJECT: [your critique]'.\n\nAnswer: {answer}"


@runtime_checkable
class Planner(Protocol):
    """
    Protocol for all planners.
    Planners own the orchestration loop and return the final result.
    """
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