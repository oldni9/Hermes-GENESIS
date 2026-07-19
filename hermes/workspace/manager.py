"""
===============================================================================
Workspace Manager
===============================================================================

Dependencies:
    - hermes.workspace.workspace

Consumes:
    - Workspace

Produces:
    - WorkspaceManager

Public API:
    - WorkspaceManager
===============================================================================
"""

from __future__ import annotations

from typing import Dict, List, Optional

from hermes.workspace.workspace import Workspace


class WorkspaceManager:
    """
    Manages the lifecycle of Workspaces.
    Initially in-memory.
    """
    
    def __init__(self) -> None:
        self._workspaces: Dict[str, Workspace] = {}

    def create_workspace(self, workspace_id: Optional[str] = None) -> Workspace:
        """Create and register a new workspace."""
        ws = Workspace(workspace_id=workspace_id)
        if ws.workspace_id in self._workspaces:
            raise ValueError(f"Workspace '{ws.workspace_id}' already exists.")
        self._workspaces[ws.workspace_id] = ws
        return ws

    def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        """Retrieve a workspace by ID."""
        return self._workspaces.get(workspace_id)

    def delete_workspace(self, workspace_id: str) -> bool:
        """Delete a workspace by ID."""
        return self._workspaces.pop(workspace_id, None) is not None

    def list_workspaces(self) -> List[Workspace]:
        """List all registered workspaces."""
        return list(self._workspaces.values())