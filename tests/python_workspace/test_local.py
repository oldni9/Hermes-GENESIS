"""
===============================================================================
Tests for Local Python Workspace
===============================================================================
"""

import pytest
import os
import sys
import time
from unittest.mock import MagicMock, patch

from hermes.sandbox import LocalSandbox
from hermes.terminal import LocalTerminal, Terminal, TerminalSession, TerminalRequest, TerminalResult
from hermes.python_workspace import (
    LocalPythonWorkspace, PythonWorkspace, PythonSession, PythonRequest
)
from hermes.python_workspace.local import _quote_arg

def test_package_exports():
    """Verify that the package exports the expected classes."""
    from hermes.python_workspace import LocalPythonWorkspace
    assert LocalPythonWorkspace is not None

@pytest.fixture
def sandbox():
    return LocalSandbox()

@pytest.fixture
def terminal(sandbox):
    return LocalTerminal(sandbox)

@pytest.fixture
def py_workspace(terminal):
    return LocalPythonWorkspace(terminal)

def test_workspace_implements_protocol(py_workspace):
    """Verify that LocalPythonWorkspace is recognized as a PythonWorkspace."""
    assert isinstance(py_workspace, PythonWorkspace)

def test_session_implements_protocol(py_workspace):
    """Verify that LocalPythonSession is recognized as a PythonSession."""
    session = py_workspace.create_session()
    assert isinstance(session, PythonSession)

def test_create_session_defaults(py_workspace):
    """Test session creation with default values."""
    session = py_workspace.create_session()
    assert session.python_executable == sys.executable

def test_run_success(py_workspace):
    """Test successful Python execution."""
    session = py_workspace.create_session()
    req = PythonRequest(source="print('Hello Python')")
    
    result = session.run(req)
    
    assert result.success
    assert "Hello Python" in result.stdout
    assert result.exit_code == 0

def test_run_syntax_error(py_workspace):
    """Test that syntax errors are captured."""
    session = py_workspace.create_session()
    req = PythonRequest(source="print('Hello")
    
    result = session.run(req)
    
    assert not result.success
    assert result.exit_code != 0
    assert "SyntaxError" in result.stderr

def test_run_runtime_exception(py_workspace):
    """Test that runtime exceptions are captured."""
    session = py_workspace.create_session()
    req = PythonRequest(source="x = 1 / 0")
    
    result = session.run(req)
    
    assert not result.success
    assert result.exit_code != 0
    assert "ZeroDivisionError" in result.stderr

def test_timeout_propagation(py_workspace):
    """Test that Python execution respects timeout."""
    session = py_workspace.create_session()
    # FIX: Use a 3-second sleep so Windows pipe cleanup doesn't block too long
    req = PythonRequest(source="import time; time.sleep(3)", timeout=1.0)
    
    start = time.time()
    result = session.run(req)
    duration = time.time() - start
    
    assert not result.success
    assert result.timed_out
    assert duration < 5.0

def test_run_pip_success(py_workspace):
    """Test successful pip command (list installed packages)."""
    session = py_workspace.create_session()
    result = session.run_pip(args=["list"])
    
    assert result.success
    assert len(result.stdout) > 0

def test_run_pip_failure(py_workspace):
    """Test that pip install of a non-existent package fails."""
    session = py_workspace.create_session()
    result = session.run_pip(args=["install", "package_that_does_not_exist_xyz_12345"])
    
    assert not result.success
    assert result.exit_code != 0

def test_run_pip_timeout():
    """Test that pip command respects timeout via mocked Terminal."""
    mock_term = MagicMock(spec=Terminal)
    mock_session = MagicMock(spec=TerminalSession)
    mock_term.create_session.return_value = mock_session
    
    mock_session.run.return_value = TerminalResult(
        success=False, stdout="", stderr="", exit_code=-1, duration=1.0, timed_out=True
    )
    
    py_ws = LocalPythonWorkspace(mock_term)
    session = py_ws.create_session()
    
    result = session.run_pip(args=["install", "requests"], timeout=1.0)
    assert result.timed_out
    assert not result.success

def test_run_pip_execution_id_propagation():
    """Test that execution_id is propagated in run_pip."""
    mock_term = MagicMock(spec=Terminal)
    mock_session = MagicMock(spec=TerminalSession)
    mock_term.create_session.return_value = mock_session
    
    mock_session.run.return_value = TerminalResult(
        success=True, stdout="", stderr="", exit_code=0, duration=0.1, timed_out=False
    )
    
    py_ws = LocalPythonWorkspace(mock_term)
    session = py_ws.create_session()
    
    exec_id = "exec_123"
    result = session.run_pip(args=["list"], execution_id=exec_id)
    assert result.execution_id == exec_id

@patch("hermes.python_workspace.local.os.path.exists", return_value=True)
@patch("hermes.python_workspace.local.os.remove")
@patch("hermes.python_workspace.local.os.fdopen")
@patch("hermes.python_workspace.local.tempfile.mkstemp")
def test_command_construction(mock_mkstemp, mock_fdopen, mock_remove, mock_exists):
    """Test that the command string is constructed exactly as expected without touching the real FS."""
    # Mock mkstemp to return a deterministic path and a dummy file descriptor
    fake_temp_path = "/tmp/fake_script.py"
    mock_mkstemp.return_value = (123, fake_temp_path)
    
    # Mock os.fdopen to return a MagicMock context manager
    mock_file = MagicMock()
    mock_fdopen.return_value.__enter__.return_value = mock_file
    
    mock_term = MagicMock(spec=Terminal)
    mock_session = MagicMock(spec=TerminalSession)
    mock_term.create_session.return_value = mock_session
    
    mock_session.run.return_value = TerminalResult(
        success=True, stdout="", stderr="", exit_code=0, duration=0.1, timed_out=False
    )
    
    py_ws = LocalPythonWorkspace(mock_term)
    fake_exe = "/custom/venv/bin/python"
    session = py_ws.create_session(python_executable=fake_exe)
    
    req = PythonRequest(source="print('Hello')")
    session.run(req)
    
    # Verify the file was written to
    mock_file.write.assert_called_once_with("print('Hello')")
    
    # Verify the exact expected command string passed to the terminal session
    actual_term_req = mock_session.run.call_args[0][0]
    assert isinstance(actual_term_req, TerminalRequest)
    
    expected_cmd = f"{_quote_arg(fake_exe)} {_quote_arg(fake_temp_path)}"
    assert actual_term_req.command == expected_cmd

def test_cwd_propagation(terminal, tmp_path):
    """Test that the session's cwd is used as the working directory."""
    py_ws = LocalPythonWorkspace(terminal)
    session = py_ws.create_session(cwd=str(tmp_path))
    
    req = PythonRequest(source="import os; print('MARKER_START'); print(os.getcwd()); print('MARKER_END')")
    result = session.run(req)
    
    assert result.success
    
    lines = result.stdout.strip().splitlines()
    marker_start_idx = -1
    marker_end_idx = -1
    for i, line in enumerate(lines):
        if "MARKER_START" in line:
            marker_start_idx = i
        elif "MARKER_END" in line:
            marker_end_idx = i
            break
            
    assert marker_start_idx != -1
    assert marker_end_idx != -1
    
    path_line = lines[marker_start_idx + 1].strip()
    assert os.path.normpath(path_line) == os.path.normpath(str(tmp_path))

@patch("hermes.python_workspace.local.os.path.exists", return_value=True)
@patch("hermes.python_workspace.local.os.remove")
@patch("hermes.python_workspace.local.os.fdopen")
@patch("hermes.python_workspace.local.tempfile.mkstemp")
def test_temp_file_cleanup(mock_mkstemp, mock_fdopen, mock_remove, mock_exists):
    """Test that temporary files are removed deterministically."""
    fake_temp_path = "/tmp/fake_cleanup_script.py"
    mock_mkstemp.return_value = (123, fake_temp_path)
    mock_file = MagicMock()
    mock_fdopen.return_value.__enter__.return_value = mock_file
    
    mock_term = MagicMock(spec=Terminal)
    mock_session = MagicMock(spec=TerminalSession)
    mock_term.create_session.return_value = mock_session
    
    mock_session.run.return_value = TerminalResult(
        success=True, stdout="", stderr="", exit_code=0, duration=0.1, timed_out=False
    )
    
    py_ws = LocalPythonWorkspace(mock_term)
    session = py_ws.create_session()
    
    session.run(PythonRequest(source="print('cleanup test')"))
    
    # Verify os.remove was called exactly once with the fake path
    mock_remove.assert_called_once_with(fake_temp_path)

def test_close_raises_on_run(py_workspace):
    """Test that run() raises RuntimeError after close()."""
    session = py_workspace.create_session()
    session.close()
    
    with pytest.raises(RuntimeError, match="has been closed"):
        session.run(PythonRequest(source="print('hi')"))

def test_close_is_idempotent(py_workspace):
    """Test that close() can be called multiple times without error."""
    session = py_workspace.create_session()
    session.close()
    session.close()  # Should not raise