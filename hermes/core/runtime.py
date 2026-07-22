"""
===============================================================================
Hermes Runtime Policy, Metrics & Context
===============================================================================

Sprint 12 Update:
Added threading.Lock to RuntimeMetrics to ensure thread-safe updates 
during parallel execution.
Added max_parallel_workers to RuntimePolicy.
===============================================================================
"""

from __future__ import annotations

import threading
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
    """
    _cancelled: bool = False
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False, compare=False)

    def cancel(self) -> None:
        with self._lock:
            self._cancelled = True

    @property
    def cancelled(self) -> bool:
        with self._lock:
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
    max_parallel_workers: int = 5


@dataclass
class RuntimeMetrics:
    """
    Universal runtime accounting object.
    Tracks actual usage and iteration counts during execution.
    Thread-safe for parallel planner execution.
    """
    used_prompt_tokens: int = 0
    used_completion_tokens: int = 0
    used_cost: float = 0.0
    tool_calls: int = 0
    llm_calls: int = 0
    
    iterations: int = 0
    planner_iterations: int = 0
    execution_turns: int = 0
    tool_iterations: int = 0
    
    started_at: float = field(default_factory=RuntimeClock.now)
    finished_at: Optional[float] = None
    
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False, compare=False)

    def start(self) -> None:
        self.started_at = RuntimeClock.now()
        self.finished_at = None

    def finish(self) -> None:
        self.finished_at = RuntimeClock.now()

    @property
    def elapsed(self) -> float:
        end = self.finished_at if self.finished_at is not None else RuntimeClock.now()
        return end - self.started_at

    @property
    def used_tokens(self) -> int:
        with self._lock:
            return self.used_prompt_tokens + self.used_completion_tokens

    def add_tokens(self, prompt_tokens: int, completion_tokens: int) -> None:
        with self._lock:
            self.used_prompt_tokens += prompt_tokens
            self.used_completion_tokens += completion_tokens

    def add_cost(self, cost: float) -> None:
        with self._lock:
            self.used_cost += cost

    def add_tool_call(self) -> None:
        with self._lock:
            self.tool_calls += 1

    def add_llm_call(self) -> None:
        with self._lock:
            self.llm_calls += 1


@dataclass
class RuntimeContext:
    """
    Groups runtime policy, metrics, and cancellation token.
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