"""
===============================================================================
Hermes Execution Contracts

Defines canonical behavior protocols for the execution layer.

This package establishes:
    - Execution lifecycle (start, shutdown, ready)
    - Execution engine interface (execute)
    - Execution‑scoped context (runtime information not carried in the request)
    - Minimal request protocol (so type checkers can validate)

All contracts are additive and do not define new request/response models.
Existing Hermes canonical models (AIRequest, AIResponse, ProviderRequest, etc.)
remain the source of truth for request/response data.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ExecutionRequest(Protocol):
    """
    Minimal protocol for an execution request.

    Any request object passed to ExecutionEngine.execute() must satisfy this.
    This allows static type checking without coupling to a concrete class.
    """

    @property
    def prompt(self) -> str:
        """Return the prompt text."""
        ...

    @property
    def provider(self) -> str | None:
        """Return the preferred provider, if any."""
        ...

    @property
    def model(self) -> str | None:
        """Return the preferred model, if any."""
        ...

    @property
    def options(self) -> dict[str, Any]:
        """Return generation options."""
        ...

    @property
    def metadata(self) -> dict[str, Any]:
        """Return request metadata."""
        ...


@dataclass(slots=True)
class ExecutionContext:
    """
    Execution‑scoped runtime context.

    Carries information about the execution environment that is not part of
    the request payload (e.g., session, user, timeout, priority).

    This is intentionally generic and reused across both legacy and AI systems.
    """

    request_id: str | None = None

    session_id: str | None = None

    user_id: str | None = None

    timeout: float | None = None

    priority: int = 0

    trace_id: str | None = None

    metadata: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class ExecutionLifecycle(Protocol):
    """Protocol for subsystems that own a lifecycle (start, shutdown, ready)."""

    def start(self) -> None:
        """Initialize the subsystem."""
        ...

    def shutdown(self) -> None:
        """Gracefully shut down the subsystem."""
        ...

    def is_ready(self) -> bool:
        """Return True if the subsystem is ready to accept requests."""
        ...


@runtime_checkable
class ExecutionEngine(ExecutionLifecycle, Protocol):
    """
    Protocol for the core execution engine.

    An ExecutionEngine is responsible for executing a single AI request and
    returning a response. Implementations may be RuntimeEngine, AIPipeline,
    ExecutionService, or any future orchestrator.
    """

    def execute(
        self,
        request: ExecutionRequest,
        context: ExecutionContext | None = None,
    ) -> Any:
        """
        Execute a single request.

        Parameters
        ----------
        request : ExecutionRequest
            The request object (must satisfy ExecutionRequest protocol).
        context : ExecutionContext | None, optional
            Execution context.

        Returns
        -------
        Any
            The result of execution (canonical response type depends on implementation).
        """
        ...


# =============================================================================
# Verification Block
# =============================================================================

# ✓ Contracts:
#   - ExecutionRequest (Protocol)
#   - ExecutionContext
#   - ExecutionLifecycle (Protocol)
#   - ExecutionEngine (Protocol)

# ✓ Additive only – no existing code modified.

# ✓ No duplicate request/response models.

# ✓ provider/model removed from ExecutionContext (belongs to request).

# ✓ request: Any replaced with ExecutionRequest Protocol.

# ✓ All symbols are stable, typed, and documented.
