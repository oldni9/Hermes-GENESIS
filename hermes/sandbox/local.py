"""
===============================================================================
Local Sandbox
===============================================================================

Dependencies:
    - os
    - subprocess
    - tempfile
    - time
    - uuid
    - typing
    - hermes.sandbox.base

Consumes:
    - SandboxRequest

Produces:
    - LocalSandbox
    - SandboxResult

Public API:
    - LocalSandbox

TODO (Future PRs):
    - Implement CPU/RAM limits (requires Docker/Firecracker).
    - Implement network restrictions.
===============================================================================
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
import uuid
from typing import List, Set

from hermes.sandbox.base import SandboxRequest, SandboxResult, Sandbox


class LocalSandbox(Sandbox):
    """
    Reference implementation.
    
    Future implementations:
    - DockerSandbox
    - FirecrackerSandbox
    - RemoteSandbox
    - PythonWorkspaceSandbox
    """
    
    _temp_prefix: str = "sandbox_exec_"
    SUPPORTED_LANGUAGES: Set[str] = {"python"}

    def execute(self, request: SandboxRequest) -> SandboxResult:
        start_time = time.time()
        
        if request.language.lower() not in self.SUPPORTED_LANGUAGES:
            return SandboxResult(
                success=False,
                stdout="",
                stderr="",
                exit_code=-1,
                duration=time.time() - start_time,
                timed_out=False,
                failure_reason=f"Unsupported language: {request.language}"
            )
            
        fd, temp_path = tempfile.mkstemp(suffix=".py", prefix=self._temp_prefix)
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(request.source)
                
            cmd = self._build_command(temp_path)
            
            try:
                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=request.timeout,
                    check=False
                )
                duration = time.time() - start_time
                
                return SandboxResult(
                    success=process.returncode == 0,
                    stdout=process.stdout,
                    stderr=process.stderr,
                    exit_code=process.returncode,
                    duration=duration,
                    timed_out=False
                )
                
            except subprocess.TimeoutExpired as e:
                duration = time.time() - start_time
                return SandboxResult(
                    success=False,
                    stdout=e.stdout or "",
                    stderr=e.stderr or "",
                    exit_code=-1,
                    duration=duration,
                    timed_out=True,
                    failure_reason=f"Execution timed out after {request.timeout} seconds."
                )
                
            except Exception as e:
                duration = time.time() - start_time
                return SandboxResult(
                    success=False,
                    stdout="",
                    stderr=str(e),
                    exit_code=-1,
                    duration=duration,
                    timed_out=False,
                    failure_reason=f"Startup error: {str(e)}"
                )
                
        finally:
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except OSError:
                pass

    def _build_command(self, script_path: str) -> List[str]:
        """
        Future command resolver.
        
        Responsible for selecting the correct runtime executable.
        Will later support:
        - Python (venv, conda, py launcher)
        - Shell
        - Node
        - Docker
        - Firecracker
        """
        return [sys.executable, script_path]