"""
===============================================================================
Workspace Package
===============================================================================

Dependencies:
    - hermes.workspace.context
    - hermes.workspace.workspace
    - hermes.workspace.manager

Consumes:
    - None directly (re-exports)

Produces:
    - ExecutionContext
    - Workspace
    - WorkspaceManager

Public API:
    - WorkspaceManager
    - Workspace
===============================================================================
"""

from hermes.workspace.context import ExecutionContext
from hermes.workspace.workspace import Workspace
from hermes.workspace.manager import WorkspaceManager

__all__ = [
    "ExecutionContext",
    "Workspace",
    "WorkspaceManager",
]