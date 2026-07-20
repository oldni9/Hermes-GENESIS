"""
===============================================================================
Workspace
===============================================================================

Dependencies:
    - typing
    - hermes.long_term_memory.manager
    - hermes.workspace.context
    - hermes.filesystem.base
    - hermes.artifacts.base
    - hermes.terminal.base

Consumes:
    - MemoryManager
    - Filesystem
    - ArtifactRegistry
    - Terminal

Produces:
    - Workspace

Public API:
    - Workspace
===============================================================================
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from hermes.artifacts.base import ArtifactRegistry
from hermes.filesystem.base import Filesystem
from hermes.long_term_memory.manager import MemoryManager
from hermes.terminal.base import Terminal
from hermes.workspace.context import ExecutionContext


class Workspace:
    """
    An isolated runtime environment for an agent.
    Acts as a composition root, holding memory, execution history, and runtime handles.
    """
    
    def __init__(
        self, 
        workspace_id: Optional[str] = None, 
        memory_manager: Optional[MemoryManager] = None,
        filesystem: Optional[Filesystem] = None,
        artifact_registry: Optional[ArtifactRegistry] = None,
        terminal: Optional[Terminal] = None
    ) -> None:
        self.workspace_id = workspace_id or f"ws_{uuid.uuid4().hex}"
        self._memory_manager = memory_manager or MemoryManager()
        self._filesystem = filesystem
        self._artifact_registry = artifact_registry
        self._terminal = terminal
        self._execution_history: List[ExecutionContext] = []
        self._config: Dict[str, Any] = {}

    @property
    def memory(self) -> MemoryManager:
        return self._memory_manager

    @property
    def filesystem(self) -> Optional[Filesystem]:
        return self._filesystem

    @property
    def artifact_registry(self) -> Optional[ArtifactRegistry]:
        return self._artifact_registry

    @property
    def terminal(self) -> Optional[Terminal]:
        return self._terminal

    @property
    def execution_history(self) -> List[ExecutionContext]:
        return list(self._execution_history)

    def create_execution(self, metadata: Optional[Dict[str, Any]] = None) -> ExecutionContext:
        """Create a new ExecutionContext for this workspace and store it in history."""
        context = ExecutionContext.create(workspace_id=self.workspace_id, metadata=metadata)
        self._execution_history.append(context)
        return context

    def get_execution(self, execution_id: str) -> Optional[ExecutionContext]:
        """Retrieve a specific execution context by ID."""
        for ctx in self._execution_history:
            if ctx.execution_id == execution_id:
                return ctx
        return None