"""
===============================================================================
Tool Runner
===============================================================================

Dependencies:
    - hermes.ai.adapters.provider_tool_adapter
    - hermes.ai.tool
    - hermes.ai.response

Consumes:
    - ToolManager
    - list[ToolCall] (from AIResponse)
    - ToolContext (built by AgentContextFactory)

Produces:
    - list[ToolResult]

Public API:
    - ToolRunner.execute()
===============================================================================
"""

from __future__ import annotations

from typing import List, Optional

from hermes.ai.adapters.provider_tool_adapter import ProviderToolAdapter
from hermes.ai.response import ToolCall
from hermes.ai.tool import ToolManager, ToolResult, ToolStatus, ToolContext


class ToolRunner:
    """
    Thin adapter that handles tool execution and result normalization.
    """

    def __init__(self, tool_manager: ToolManager) -> None:
        self._tool_manager = tool_manager

    def execute(
        self, 
        provider_tool_calls: List[ToolCall], 
        context: Optional[ToolContext] = None
    ) -> List[ToolResult]:
        """
        Execute a batch of provider tool calls and return results mapped by call_id.
        """
        converted_calls, conversion_errors = ProviderToolAdapter.convert_provider_tool_calls(
            provider_tool_calls
        )

        if converted_calls:
            results = self._tool_manager.execute_batch(converted_calls, context=context)
        else:
            results = []

        all_results = {r.call_id: r for r in results}
        for err in conversion_errors:
            all_results[err.call_id] = err

        ordered_results: List[ToolResult] = []
        for tc in provider_tool_calls:
            result = all_results.get(tc.id)
            if result is None:
                ordered_results.append(ToolResult(
                    call_id=tc.id,
                    status=ToolStatus.FAILED,
                    error="Error: Tool execution result missing.",
                ))
            else:
                ordered_results.append(result)

        return ordered_results