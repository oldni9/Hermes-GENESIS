"""
===============================================================================
Tool Validation
===============================================================================

Dependencies:
    - enum
    - dataclasses
    - typing
    - hermes.ai.response
    - hermes.ai.tool

Consumes:
    - ToolCall
    - ToolRegistry

Produces:
    - ToolValidationStatus
    - ToolValidationResult
    - ToolValidator

Public API:
    - ToolValidator
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from hermes.ai.response import ToolCall
from hermes.ai.tool import ToolRegistry


class ToolValidationStatus(str, Enum):
    """Hierarchy of tool validation results."""
    VALID = "valid"
    UNKNOWN_TOOL = "unknown_tool"
    DISABLED_TOOL = "disabled_tool"
    MALFORMED_ARGUMENTS = "malformed_arguments"


@dataclass
class ToolValidationResult:
    """The result of validating a single tool call."""
    status: ToolValidationStatus
    reason: str = ""
    tool_call: Optional[ToolCall] = None


class ToolValidator:
    """
    Validates tool calls against the ToolRegistry without executing them.
    """

    def __init__(self, registry: ToolRegistry) -> None:
        self._registry = registry

    def validate_batch(self, calls: List[ToolCall]) -> List[ToolValidationResult]:
        """Validate a batch of tool calls."""
        results = []
        for call in calls:
            results.append(self._validate_single(call))
        return results

    def _validate_single(self, call: ToolCall) -> ToolValidationResult:
        """Validate a single tool call."""
        if not call.function:
            return ToolValidationResult(
                status=ToolValidationStatus.MALFORMED_ARGUMENTS,
                reason="No function specified in tool call.",
                tool_call=call
            )

        name = call.function.name
        tool = self._registry.get(name)

        if tool is None:
            return ToolValidationResult(
                status=ToolValidationStatus.UNKNOWN_TOOL,
                reason=f"Tool '{name}' is not registered.",
                tool_call=call
            )

        if not tool.enabled:
            return ToolValidationResult(
                status=ToolValidationStatus.DISABLED_TOOL,
                reason=f"Tool '{name}' is currently disabled.",
                tool_call=call
            )

        args = call.function.arguments
        if not isinstance(args, (dict, str)):
            return ToolValidationResult(
                status=ToolValidationStatus.MALFORMED_ARGUMENTS,
                reason=f"Arguments for '{name}' must be a dict or JSON string.",
                tool_call=call
            )

        return ToolValidationResult(
            status=ToolValidationStatus.VALID,
            tool_call=call
        )