"""
===============================================================================
Local Sandbox
===============================================================================

Dependencies:
    - os
    - subprocess
    - sys
    - tempfile
    - time
    - uuid
    - typing
    - hermes.sandbox.base

Consumes:
    - SandboxRequest

Produces:
    - LocalSandbox

Public API:
    - LocalSandbox
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
    """
    
    _temp_prefix: str = "sandbox_exec_"
    SUPPORTED_LANGUAGES: Set[str] = {"python", "shell"}

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
            
        # FIX: Correct file extensions for Windows shell compatibility
        is_windows = sys.platform == "win32"
        if request.language == "shell":
            suffix = ".bat" if is_windows else ".sh"
        else:
            suffix = ".py"
            
        fd, temp_path = tempfile.mkstemp(suffix=suffix, prefix=self._temp_prefix)
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(request.source)
                
            cmd = self._build_command(temp_path, request.language)
            
            process_env = os.environ.copy()
            if request.env:
                process_env.update(request.env)
            
            try:
                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=request.timeout,
                    check=False,
                    cwd=request.cwd,
                    env=process_env
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

    def _build_command(self, script_path: str, language: str) -> List[str]:
        """
        Future command resolver. 
        TODO: Extract to a CommandResolver interface to support multiple runtimes cleanly.
        """
        if language == "python":
            return [sys.executable, script_path]
        elif language == "shell":
            # FIX: Correct Windows shell invocation
            if sys.platform == "win32":
                return ["cmd.exe", "/c", script_path]
            return ["/bin/sh", script_path]
        else:
            return [sys.executable, script_path]