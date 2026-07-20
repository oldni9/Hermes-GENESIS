"""
===============================================================================
Local Terminal
===============================================================================

Dependencies:
    - os
    - time
    - uuid
    - typing
    - hermes.sandbox.base
    - hermes.terminal.base

Consumes:
    - Sandbox
    - TerminalRequest

Produces:
    - LocalTerminal
    - LocalTerminalSession

Public API:
    - LocalTerminal
===============================================================================
"""

from __future__ import annotations

import os
import time
import uuid
from typing import Dict, Optional

from hermes.sandbox.base import Sandbox, SandboxRequest
from hermes.terminal.base import Terminal, TerminalRequest, TerminalResult, TerminalSession


class LocalTerminalSession(TerminalSession):
    """
    A stateful terminal session that orchestrates shell execution via Sandbox.
    Does not parse shell commands. Maintains cwd and env state to pass to Sandbox.
    """
    
    def __init__(self, sandbox: Sandbox, cwd: str = ".", env: Optional[Dict[str, str]] = None) -> None:
        self._sandbox = sandbox
        self._cwd = os.path.abspath(cwd)
        self._env = dict(env) if env else {}
        self._session_id = f"sess_{uuid.uuid4().hex}"
        self._closed = False

    @property
    def session_id(self) -> str:
        return self._session_id

    @property
    def cwd(self) -> str:
        return self._cwd

    @property
    def env(self) -> Dict[str, str]:
        return dict(self._env)

    def run(self, request: TerminalRequest) -> TerminalResult:
        if self._closed:
            raise RuntimeError(f"Terminal session {self._session_id} has been closed.")
            
        start_time = time.time()
        
        sandbox_req = SandboxRequest(
            language="shell",
            source=request.command,
            timeout=request.timeout,
            cwd=self._cwd,
            env=self._env
        )
        
        sandbox_res = self._sandbox.execute(sandbox_req)
        
        return TerminalResult(
            success=sandbox_res.success,
            stdout=sandbox_res.stdout,
            stderr=sandbox_res.stderr,
            exit_code=sandbox_res.exit_code,
            duration=sandbox_res.duration,
            timed_out=sandbox_res.timed_out
        )

    def close(self) -> None:
        """
        Clean up session resources.
        Currently a no-op for LocalSandbox, but required for future PTY/SSH backends.
        """
        self._closed = True


class LocalTerminal(Terminal):
    """
    Factory for creating LocalTerminalSessions.
    """
    
    def __init__(self, sandbox: Sandbox) -> None:
        self._sandbox = sandbox

    def create_session(
        self, 
        cwd: str = ".", 
        env: Optional[Dict[str, str]] = None
    ) -> TerminalSession:
        return LocalTerminalSession(self._sandbox, cwd, env)