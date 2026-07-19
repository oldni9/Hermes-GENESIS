"""
===============================================================================
Workspace
===============================================================================

Dependencies:
    - typing
    - hermes.long_term_memory.manager
    - hermes.workspace.context

Consumes:
    - MemoryManager

Produces:
    - Workspace

Public API:
    - Workspace
===============================================================================
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from hermes.long_term_memory.manager import MemoryManager
from hermes.workspace.context import ExecutionContext


class Workspace:
    """
    An isolated runtime environment for an agent.
    Acts as a composition root, holding memory, execution history, and future runtime handles.
    """
    
    def __init__(self, workspace_id: Optional[str] = None, memory_manager: Optional[MemoryManager] = None) -> None:
        self.workspace_id = workspace_id or f"ws_{uuid.uuid4().hex}"
        self._memory_manager = memory_manager or MemoryManager()
        self._execution_history: List[ExecutionContext] = []
        self._config: Dict[str, Any] = {}
        
        # Placeholder for future filesystem handle
        # self.filesystem = None 

    @property
    def memory(self) -> MemoryManager:
        return self._memory_manager

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