"""
===============================================================================
Python Workspace Base
===============================================================================

Dependencies:
    - dataclasses
    - typing

Consumes:
    - None

Produces:
    - PythonRequest
    - PythonResult
    - PythonSession
    - PythonWorkspace

Public API:
    - PythonWorkspace
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Protocol, runtime_checkable


@dataclass(frozen=True)
class PythonRequest:
    """
    Immutable request to run Python source code.
    """
    source: str
    timeout: float = 30.0
    execution_id: Optional[str] = None


@dataclass(frozen=True)
class PythonResult:
    """
    Immutable result of a Python execution.
    """
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    duration: float
    timed_out: bool
    execution_id: Optional[str] = None


@runtime_checkable
class PythonSession(Protocol):
    """
    Protocol for a stateful Python execution session.
    """
    @property
    def python_executable(self) -> str:
        ...
        
    def run(self, request: PythonRequest) -> PythonResult:
        ...
        
    def run_pip(self, args: List[str], timeout: float = 60.0, execution_id: Optional[str] = None) -> PythonResult:
        ...

    def close(self) -> None:
        ...


@runtime_checkable
class PythonWorkspace(Protocol):
    """
    Protocol for Python workspace factories.
    """
    def create_session(
        self, 
        python_executable: str = "python", 
        cwd: str = ".", 
        env: Optional[Dict[str, str]] = None
    ) -> PythonSession:
        ...