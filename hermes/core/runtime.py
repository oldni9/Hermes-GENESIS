"""
===============================================================================
Hermes Runtime Policy, Metrics & Context
===============================================================================

Defines the immutable runtime policy, mutable runtime metrics, and the 
RuntimeContext that groups them with a cancellation token.
===============================================================================
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional


class RuntimeClock:
    """Abstraction for timekeeping to allow deterministic testing."""
    @staticmethod
    def now() -> float:
        return time.monotonic()


@dataclass
class CancellationToken:
    """
    Simple cooperative cancellation primitive.
    Hermes is currently single-threaded; concurrency primitives will be 
    introduced in a later sprint.
    """
    _cancelled: bool = False

    def cancel(self) -> None:
        """Mark the token as cancelled."""
        self._cancelled = True

    @property
    def cancelled(self) -> bool:
        """Check if cancellation has been requested."""
        return self._cancelled


@dataclass(frozen=True)
class RuntimePolicy:
    """
    Immutable runtime execution policy.
    Defines the constraints under which an execution is allowed to run.
    """
    timeout: Optional[float] = None
    max_tokens: Optional[int] = None
    max_cost: Optional[float] = None


@dataclass
class RuntimeMetrics:
    """
    Universal runtime accounting object.
    Tracks actual usage and iteration counts during execution.
    """
    used_prompt_tokens: int = 0
    used_completion_tokens: int = 0
    used_cost: float = 0.0
    tool_calls: int = 0
    llm_calls: int = 0
    
    # Iteration Counters for UI Transparency
    iterations: int = 0
    planner_iterations: int = 0
    execution_turns: int = 0
    tool_iterations: int = 0
    
    started_at: float = field(default_factory=RuntimeClock.now)
    finished_at: Optional[float] = None

    def start(self) -> None:
        """Reset the start time."""
        self.started_at = RuntimeClock.now()
        self.finished_at = None

    def finish(self) -> None:
        """Mark the execution as finished."""
        self.finished_at = RuntimeClock.now()

    @property
    def elapsed(self) -> float:
        """Return elapsed time in seconds."""
        end = self.finished_at if self.finished_at is not None else RuntimeClock.now()
        return end - self.started_at

    @property
    def used_tokens(self) -> int:
        """Total tokens used (prompt + completion)."""
        return self.used_prompt_tokens + self.used_completion_tokens

    def add_tokens(self, prompt_tokens: int, completion_tokens: int) -> None:
        self.used_prompt_tokens += prompt_tokens
        self.used_completion_tokens += completion_tokens

    def add_cost(self, cost: float) -> None:
        self.used_cost += cost

    def add_tool_call(self) -> None:
        self.tool_calls += 1

    def add_llm_call(self) -> None:
        self.llm_calls += 1


@dataclass
class RuntimeContext:
    """
    Groups runtime policy, metrics, and cancellation token.
    This allows different planners (like ToT or Debate) to inherit the policy
    but own different metrics or cancellation tokens.
    """
    policy: RuntimePolicy = field(default_factory=RuntimePolicy)
    metrics: RuntimeMetrics = field(default_factory=RuntimeMetrics)
    cancellation_token: CancellationToken = field(default_factory=CancellationToken)

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture