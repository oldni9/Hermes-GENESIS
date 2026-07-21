from __future__ import annotations

from typing import Any, Dict, List, Optional

from hermes.ai.tool import (
    ToolCall,
    ToolContext,
    ToolManager as BaseToolManager,
    ToolStatus,
)

from hermes.tools.base import ToolExecutionResult


class ToolManager(BaseToolManager):
    """
    Compatibility wrapper around hermes.ai.tool.ToolManager.

    Keeps the legacy API used by Workspace and the rest of Hermes.
    """

    @property
    def registry(self):
        return self._registry

    #
    # ------------------------------------------------------------------
    # Legacy execution API
    # ------------------------------------------------------------------
    #

    def execute_tool(
        self,
        tool_name: str,
        args: Dict[str, Any],
        context: Optional[ToolContext] = None,
        timeout: Optional[float] = None,
    ) -> ToolExecutionResult:

        call = ToolCall(
            tool_name=tool_name,
            arguments=args,
        )

        result = self.execute(
            call,
            context=context,
            timeout=timeout,
        )

        return ToolExecutionResult(
            success=result.status == ToolStatus.SUCCESS,
            output=result.output,
            error=result.error,
            duration=result.duration,
            tool_name=tool_name,
            execution_id=(
                context.metadata.get("execution_id")
                if context
                else None
            ),
        )

    #
    # ------------------------------------------------------------------
    # Compatibility helpers
    # ------------------------------------------------------------------
    #

    def validate_arguments(
        self,
        tool_name: str,
        args: Dict[str, Any],
    ) -> bool:

        try:
            tool = self.get_tool(tool_name)
            self._validate_arguments(tool, args)
            return True
        except Exception:
            return False

    #
    # ------------------------------------------------------------------
    # Registry wrappers
    # ------------------------------------------------------------------
    #

    def exists(self, name: str) -> bool:
        return self._registry.exists(name)

    def full_names(self) -> List[str]:
        return self._registry.full_names()

    def unregister(self, name: str) -> None:
        """
        Workspace expects ToolManager.unregister().
        """
        self._registry.unregister(name)

    def unregister_tool(self, name: str) -> None:
        """
        Older compatibility alias.
        """
        self.unregister(name)