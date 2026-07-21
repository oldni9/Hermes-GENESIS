"""
===============================================================================
Local Python Workspace
===============================================================================

Dependencies:
    - os
    - sys
    - shlex
    - subprocess
    - tempfile
    - time
    - logging
    - typing
    - hermes.terminal.base
    - hermes.python_workspace.base

Consumes:
    - Terminal
    - TerminalRequest
    - PythonRequest

Produces:
    - LocalPythonWorkspace
    - LocalPythonSession

Public API:
    - LocalPythonWorkspace

Technical Debt Notes:
1. Temporary Files: This implementation creates temporary `.py` files in the
   OS temp directory to execute scripts. Tracebacks and relative imports will
   reference this system path, not the workspace cwd. Future refactoring should
   push script materialization down into the Sandbox layer.

2. Shell Quoting: TerminalRequest currently only accepts `command: str`.
   This forces us to manually quote arguments. We use `subprocess.list2cmdline`
   for Windows and `shlex.quote` for POSIX, which are robust. True architectural
   cleanliness will come when TerminalRequest supports structured `argv: list[str]`.
===============================================================================
"""

from __future__ import annotations

import os
import sys
import shlex
import subprocess
import tempfile
import time
import logging
from typing import Dict, List, Optional

from hermes.terminal.base import Terminal, TerminalRequest
from hermes.python_workspace.base import (
    PythonRequest, PythonResult, PythonSession, PythonWorkspace
)

logger = logging.getLogger(__name__)

def _quote_arg(arg: str) -> str:
    """
    Robust cross-platform shell argument quoting.
    TODO: Remove this entirely once TerminalRequest supports `argv: list[str]`.
    """
    if sys.platform == "win32":
        # Use subprocess.list2cmdline for robust Windows quoting
        return subprocess.list2cmdline([arg])
    else:
        return shlex.quote(arg)


class LocalPythonSession(PythonSession):
    """
    A stateful Python session that delegates execution to the Terminal.
    """
    
    def __init__(
        self, 
        terminal: Terminal, 
        python_executable: str, 
        cwd: str = ".", 
        env: Optional[Dict[str, str]] = None
    ) -> None:
        self._terminal = terminal
        self._python_executable = python_executable
        self._session = terminal.create_session(cwd=cwd, env=env)
        self._closed = False

    @property
    def python_executable(self) -> str:
        return self._python_executable

    def run(self, request: PythonRequest) -> PythonResult:
        if self._closed:
            raise RuntimeError("PythonSession has been closed.")
            
        start_time = time.time()
        
        # Create a temporary file to hold the source code
        fd, temp_path = tempfile.mkstemp(suffix=".py", prefix="python_exec_")
        try:
            # Explicitly use UTF-8 and LF newlines for cross-platform safety
            with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as f:
                f.write(request.source)
                
            quoted_exe = _quote_arg(self._python_executable)
            quoted_path = _quote_arg(temp_path)
            cmd = f"{quoted_exe} {quoted_path}"
                
            term_req = TerminalRequest(command=cmd, timeout=request.timeout)
            
            term_res = self._session.run(term_req)
            
            return PythonResult(
                success=term_res.success,
                stdout=term_res.stdout,
                stderr=term_res.stderr,
                exit_code=term_res.exit_code,
                duration=term_res.duration,
                timed_out=term_res.timed_out,
                execution_id=request.execution_id
            )
        finally:
            self._safe_cleanup(temp_path)

    def run_pip(self, args: List[str], timeout: float = 60.0, execution_id: Optional[str] = None) -> PythonResult:
        """Execute a pip command."""
        if self._closed:
            raise RuntimeError("PythonSession has been closed.")
            
        quoted_exe = _quote_arg(self._python_executable)
        quoted_args = " ".join(_quote_arg(arg) for arg in args)
        cmd = f"{quoted_exe} -m pip {quoted_args}"
        
        term_req = TerminalRequest(command=cmd, timeout=timeout)
        term_res = self._session.run(term_req)
        
        return PythonResult(
            success=term_res.success,
            stdout=term_res.stdout,
            stderr=term_res.stderr,
            exit_code=term_res.exit_code,
            duration=term_res.duration,
            timed_out=term_res.timed_out,
            execution_id=execution_id
        )

    def close(self) -> None:
        """
        Clean up session resources.
        This action is irreversible. A closed session cannot be reopened.
        """
        # Make close() idempotent
        if self._closed:
            return
        self._closed = True
        self._session.close()

    def _safe_cleanup(self, path: str, retries: int = 3, delay: float = 0.1) -> None:
        """Attempt to delete a file with retries to handle OS locking."""
        for i in range(retries):
            try:
                if os.path.exists(path):
                    os.remove(path)
                break
            except PermissionError:
                if i < retries - 1:
                    time.sleep(delay)
                else:
                    # If it still fails after retries, log the issue and leave it
                    # to the OS temp cleanup mechanisms.
                    logger.warning(f"Failed to clean up temporary file after {retries} retries: {path}")


class LocalPythonWorkspace(PythonWorkspace):
    """
    Factory for creating LocalPythonSessions.
    """
    
    def __init__(self, terminal: Terminal) -> None:
        self._terminal = terminal

    def create_session(
        self, 
        python_executable: str = "python", 
        cwd: str = ".", 
        env: Optional[Dict[str, str]] = None
    ) -> PythonSession:
        exe = python_executable if python_executable != "python" else sys.executable
        return LocalPythonSession(self._terminal, exe, cwd, env)