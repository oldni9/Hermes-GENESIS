"""
===============================================================================
Terminal Package
===============================================================================

Dependencies:
    - hermes.terminal.base
    - hermes.terminal.local

Consumes:
    - None directly (re-exports)

Produces:
    - TerminalRequest
    - TerminalResult
    - TerminalSession
    - Terminal
    - LocalTerminal

Public API:
    - LocalTerminal
===============================================================================
"""

from hermes.terminal.base import TerminalRequest, TerminalResult, TerminalSession, Terminal
from hermes.terminal.local import LocalTerminal

__all__ = [
    "TerminalRequest",
    "TerminalResult",
    "TerminalSession",
    "Terminal",
    "LocalTerminal",
]