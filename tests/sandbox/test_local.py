"""
===============================================================================
Tests for Local Sandbox
===============================================================================
"""

import pytest
import time
import os
import glob
import tempfile

from hermes.sandbox import LocalSandbox, SandboxRequest, Sandbox


@pytest.fixture
def sandbox():
    return LocalSandbox()

def test_sandbox_implements_protocol(sandbox):
    """Verify that LocalSandbox is recognized as a Sandbox."""
    assert isinstance(sandbox, Sandbox)

def test_successful_execution(sandbox):
    """Test that valid Python code executes successfully."""
    request = SandboxRequest(
        language="python",
        source="print('Hello Sandbox')",
        timeout=5.0
    )
    
    result = sandbox.execute(request)
    
    assert result.success
    assert "Hello Sandbox" in result.stdout
    assert result.exit_code == 0
    assert not result.timed_out
    assert result.failure_reason is None
    # FIX: Future-proof assertion for execution_id
    assert result.execution_id is None or result.execution_id.startswith("exec_")

def test_stderr_capture(sandbox):
    """Test that stderr is captured on runtime errors."""
    request = SandboxRequest(
        language="python",
        source="import sys; sys.stderr.write('Error message\\n'); exit(1)",
        timeout=5.0
    )
    
    result = sandbox.execute(request)
    
    assert not result.success
    assert "Error message" in result.stderr
    assert result.exit_code == 1
    assert not result.timed_out

def test_timeout_enforcement(sandbox):
    """Test that execution is killed and reported as timed out."""
    request = SandboxRequest(
        language="python",
        source="import time; time.sleep(10)",
        timeout=1.0
    )
    
    start = time.time()
    result = sandbox.execute(request)
    duration = time.time() - start
    
    assert not result.success
    assert result.timed_out
    assert result.exit_code == -1
    assert "timed out" in result.failure_reason.lower()
    assert duration < 5.0

def test_unsupported_language(sandbox):
    """Test that unsupported languages are rejected cleanly."""
    request = SandboxRequest(
        language="javascript",
        source="console.log('Hello')",
        timeout=5.0
    )
    
    result = sandbox.execute(request)
    
    assert not result.success
    assert result.exit_code == -1
    assert "Unsupported language" in result.failure_reason

def test_temp_file_cleanup(sandbox):
    """Test that temporary files are removed after execution."""
    request = SandboxRequest(
        language="python",
        source="print('cleanup test')",
        timeout=5.0
    )
    
    sandbox.execute(request)
    
    temp_dir = tempfile.gettempdir()
    # FIX: Use the exact prefix exposed by LocalSandbox
    leftover_files = glob.glob(os.path.join(temp_dir, f"{sandbox._temp_prefix}*.py"))
    
    assert len(leftover_files) == 0, f"Temporary files were not cleaned up: {leftover_files}"