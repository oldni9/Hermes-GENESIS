"""
===============================================================================
Workspace
===============================================================================
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional, Set

from hermes.artifacts.base import ArtifactRegistry
from hermes.filesystem.base import Filesystem
from hermes.long_term_memory.manager import MemoryManager
from hermes.python_workspace.base import PythonWorkspace
from hermes.terminal.base import Terminal
from hermes.workspace.context import ExecutionContext
from hermes.tools.manager import ToolManager
from hermes.tools.builtin import FileTools
from hermes.ai.tool import Tool, ToolError


class Workspace:
    def __init__(
        self,
        workspace_id: Optional[str] = None,
        memory_manager: Optional[MemoryManager] = None,
        filesystem: Optional[Filesystem] = None,
        artifact_registry: Optional[ArtifactRegistry] = None,
        terminal: Optional[Terminal] = None,
        python_workspace: Optional[PythonWorkspace] = None,
        tool_manager: Optional[ToolManager] = None,
    ) -> None:
        self.workspace_id = workspace_id or f"ws_{uuid.uuid4().hex}"
        self._memory_manager = memory_manager or MemoryManager()
        self._filesystem = filesystem
        self._artifact_registry = artifact_registry
        self._terminal = terminal
        self._python_workspace = python_workspace
        self._tool_manager = tool_manager
        self._execution_history: List[ExecutionContext] = []
        self._config: Dict[str, Any] = {}
        self._closed = False
        self._registered_tool_names: Set[str] = set()

        if (
            self._filesystem is not None
            and self._tool_manager is not None
        ):
            self._register_file_tools()

    def _register_file_tools(self) -> None:
        file_tools = FileTools(self._filesystem)
        ws_prefix = self.workspace_id

        for tool in file_tools.tools:
            namespaced_tool = Tool(
                name=tool.name,
                namespace=ws_prefix,
                description=tool.description,
                parameters=tool.parameters,
                function=tool.function,
                is_async=tool.is_async,
                category=tool.category,
                enabled=tool.enabled,
                aliases=tool.aliases,
                version=tool.version,
                timeout=tool.timeout,
                retries=tool.retries,
                dangerous=tool.dangerous,
                requires_confirmation=tool.requires_confirmation,
                filesystem=tool.filesystem,
                network=tool.network,
                read_only=tool.read_only,
                metadata=tool.metadata,
            )

            full_name = namespaced_tool.full_name()

            try:
                self._tool_manager.register_tool(namespaced_tool)
                self._registered_tool_names.add(full_name)
            except ToolError:
                if self._tool_manager.exists(full_name):
                    self._registered_tool_names.add(full_name)

    def close(self) -> None:
        if self._closed:
            return

        self._closed = True

        if self._tool_manager is not None:
            for full_name in sorted(self._registered_tool_names):
                self._tool_manager.unregister(full_name)
            self._registered_tool_names.clear()

    def __enter__(self) -> "Workspace":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

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
    def python_workspace(self) -> Optional[PythonWorkspace]:
        return self._python_workspace

    @property
    def tool_manager(self) -> Optional[ToolManager]:
        return self._tool_manager

    @property
    def execution_history(self) -> List[ExecutionContext]:
        return list(self._execution_history)

    def create_execution(self, metadata: Optional[Dict[str, Any]] = None) -> ExecutionContext:
        context = ExecutionContext.create(workspace_id=self.workspace_id, metadata=metadata)
        self._execution_history.append(context)
        return context

    def get_execution(self, execution_id: str) -> Optional[ExecutionContext]:
        for ctx in self._execution_history:
            if ctx.execution_id == execution_id:
                return ctx
        return None