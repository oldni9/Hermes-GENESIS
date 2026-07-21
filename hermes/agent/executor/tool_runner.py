"""
===============================================================================
Agent Tool Runner
===============================================================================

Dependencies:
    - typing
    - hermes.ai.adapters.provider_tool_adapter
    - hermes.ai.response
    - hermes.ai.tool

Consumes:
    - ToolManager
    - list[ToolCall] (from AIResponse)
    - ToolContext

Produces:
    - Dict[str, ToolResult] (call_id -> ToolResult)

Public API:
    - ToolRunner
===============================================================================
"""

from __future__ import annotations

from typing import Dict, List

from hermes.ai.adapters.provider_tool_adapter import ProviderToolAdapter
from hermes.ai.response import ToolCall
from hermes.ai.tool import ToolContext, ToolManager, ToolResult


class ToolRunner:
    """
    Execution adapter for tools.
    Converts provider tool calls, executes them, and maps structured results by call_id.
    Does NOT serialize results to strings; preserves structured ToolResult objects.
    """

    def __init__(self, tool_manager: ToolManager) -> None:
        self._tool_manager = tool_manager

    def execute(
        self, 
        provider_tool_calls: List[ToolCall], 
        context: ToolContext
    ) -> Dict[str, ToolResult]:
        """
        Execute a batch of provider tool calls.
        
        Returns:
            A dictionary mapping `call_id` to the structured `ToolResult` object.
        """
        converted_calls, conversion_errors = ProviderToolAdapter.convert_provider_tool_calls(
            provider_tool_calls
        )

        if converted_calls:
            results = self._tool_manager.execute_batch(converted_calls, context=context)
        else:
            results = []

        # Map results back to original ToolCall order by call_id
        all_results = {r.call_id: r for r in results}
        for err in conversion_errors:
            all_results[err.call_id] = err

        # Ensure every requested call_id has an entry, even if missing
        for tc in provider_tool_calls:
            if tc.id not in all_results:
                all_results[tc.id] = ToolResult(
                    call_id=tc.id,
                    status="failed",
                    error="Error: Tool execution result missing."
                )

        return all_results