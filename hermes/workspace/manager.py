"""
===============================================================================
Workspace Manager
===============================================================================
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from hermes.workspace.workspace import Workspace

class WorkspaceManager:
    def __init__(self) -> None:
        self._workspaces: Dict[str, Workspace] = {}

    def create_workspace(self, workspace_id: Optional[str] = None, **kwargs: Any) -> Workspace:
        ws = Workspace(workspace_id=workspace_id, **kwargs)
        if ws.workspace_id in self._workspaces:
            raise ValueError(f"Workspace '{ws.workspace_id}' already exists.")
        self._workspaces[ws.workspace_id] = ws
        return ws

    def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        return self._workspaces.get(workspace_id)

    def delete_workspace(self, workspace_id: str) -> bool:
        ws = self._workspaces.pop(workspace_id, None)
        if ws is not None:
            ws.close()
            return True
        return False

    def list_workspaces(self) -> List[Workspace]:
        return list(self._workspaces.values())