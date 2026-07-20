"""
===============================================================================
Terminal Base
===============================================================================

Dependencies:
    - dataclasses
    - typing

Consumes:
    - None

Produces:
    - TerminalRequest
    - TerminalResult
    - TerminalSession
    - Terminal

Public API:
    - Terminal
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Protocol, runtime_checkable


@dataclass(frozen=True)
class TerminalRequest:
    """
    Immutable request to run a command in the terminal.
    """
    command: str
    timeout: float = 30.0


@dataclass(frozen=True)
class TerminalResult:
    """
    Immutable result of a terminal command.
    """
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    duration: float
    timed_out: bool


@runtime_checkable
class TerminalSession(Protocol):
    """
    Protocol for a stateful terminal session.
    """
    @property
    def session_id(self) -> str:
        ...
        
    @property
    def cwd(self) -> str:
        ...
        
    @property
    def env(self) -> Dict[str, str]:
        ...
        
    def run(self, request: TerminalRequest) -> TerminalResult:
        ...
        
    def close(self) -> None:
        ...


@runtime_checkable
class Terminal(Protocol):
    """
    Protocol for terminal factories.
    """
    def create_session(
        self, 
        cwd: str = ".", 
        env: Optional[Dict[str, str]] = None
    ) -> TerminalSession:
        ...