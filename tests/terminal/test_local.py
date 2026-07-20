"""
===============================================================================
Tests for Local Terminal
===============================================================================
"""

import pytest
import os
import time

from hermes.sandbox import LocalSandbox
from hermes.terminal import LocalTerminal, Terminal, TerminalSession, TerminalRequest


@pytest.fixture
def sandbox():
    return LocalSandbox()

@pytest.fixture
def terminal(sandbox):
    return LocalTerminal(sandbox)

def test_terminal_implements_protocol(terminal):
    """Verify that LocalTerminal is recognized as a Terminal."""
    assert isinstance(terminal, Terminal)

def test_create_session_defaults(terminal):
    """Test session creation with default values."""
    session = terminal.create_session()
    assert isinstance(session, TerminalSession)
    assert session.cwd == os.path.abspath(".")
    assert session.env == {}
    assert session.session_id.startswith("sess_")

def test_run_simple_command(terminal):
    """Test running a simple shell command."""
    session = terminal.create_session()
    req = TerminalRequest(command="echo Hello Terminal")
    
    result = session.run(req)
    
    assert result.success
    assert "Hello Terminal" in result.stdout
    assert result.exit_code == 0

def test_failed_command(terminal):
    """Test that a failed command returns appropriate status without corrupting session."""
    session = terminal.create_session()
    req = TerminalRequest(command="nonexistent_command_12345")
    
    result = session.run(req)
    
    assert not result.success
    assert result.exit_code != 0
    # Verify session is still usable
    req2 = TerminalRequest(command="echo Still Alive")
    res2 = session.run(req2)
    assert res2.success

def test_timeout_propagation(terminal):
    """Test that terminal propagates sandbox timeout."""
    session = terminal.create_session()
    # FIX: Use a shorter ping (3 secs) so Windows pipe cleanup doesn't block too long
    cmd = "ping -n 3 127.0.0.1 > NUL" if os.name == "nt" else "sleep 3"
    req = TerminalRequest(command=cmd, timeout=1.0)
    
    start = time.time()
    result = session.run(req)
    duration = time.time() - start
    
    assert not result.success
    assert result.timed_out
    # With a 3-second ping, the max blocking time should be around 3 seconds.
    assert duration < 5.0

def test_cwd_passed_to_sandbox(terminal, tmp_path):
    """Test that commands execute in the session's cwd."""
    test_file = tmp_path / "test_marker.txt"
    test_file.write_text("marker")
    
    session = terminal.create_session(cwd=str(tmp_path))
    req = TerminalRequest(command="dir" if os.name == "nt" else "ls")
    
    result = session.run(req)
    
    assert result.success
    assert "test_marker.txt" in result.stdout

def test_env_passed_to_sandbox(terminal):
    """Test that environment variables are passed to the execution."""
    session = terminal.create_session(env={"MY_TEST_VAR": "12345"})
    cmd = "echo %MY_TEST_VAR%" if os.name == "nt" else "echo $MY_TEST_VAR"
    req = TerminalRequest(command=cmd)
    
    result = session.run(req)
    
    assert result.success
    assert "12345" in result.stdout

def test_close_raises_on_run(terminal):
    """Test that run() raises RuntimeError after close()."""
    session = terminal.create_session()
    session.close()
    
    with pytest.raises(RuntimeError, match="has been closed"):
        session.run(TerminalRequest(command="echo test"))