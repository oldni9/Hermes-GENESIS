"""
===============================================================================
Sandbox Base
===============================================================================

Dependencies:
    - dataclasses
    - typing

Consumes:
    - None

Produces:
    - SandboxRequest
    - SandboxResult
    - Sandbox

Public API:
    - SandboxRequest
    - SandboxResult
    - Sandbox

TODO (Future PRs):
    - Support shell execution.
    - Support stdin.
    - Support environment variables.
    - Support Docker backend.
    - Support Firecracker backend.
    - Support streaming stdout.
    - Support cancellation.
    - Support working directory.
    - Support mounted workspace filesystem.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol, runtime_checkable


@dataclass(frozen=True)
class SandboxRequest:
    """
    Immutable request for sandbox execution.
    """
    language: str  # e.g., "python", "shell"
    source: str    # The code to execute
    timeout: float = 30.0


@dataclass(frozen=True)
class SandboxResult:
    """
    Immutable result of a sandbox execution.
    """
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    duration: float
    timed_out: bool
    failure_reason: Optional[str] = None
    execution_id: Optional[str] = None  # FIX: Added execution_id for future telemetry


@runtime_checkable
class Sandbox(Protocol):
    """
    Protocol for all sandbox implementations.
    Implementations must not expose execution-specific details in the public API.
    """
    def execute(self, request: SandboxRequest) -> SandboxResult:
        ...