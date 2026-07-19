"""
===============================================================================
Provider Tool Adapter

Converts tool calls from a provider response (AIResponse.tool_calls)
into internal ToolCall objects suitable for ToolManager.

This keeps ToolManager decoupled from the AI response model.
===============================================================================
"""

from __future__ import annotations

import json
from typing import Any, Sequence

from hermes.ai.response import ToolCall as ProviderToolCall
from hermes.ai.tool import ToolCall, ToolResult, ToolStatus


class ProviderToolAdapter:
    """
    Adapter for converting provider tool calls to internal representations.
    """

    @staticmethod
    def normalize_arguments(args: Any) -> dict[str, Any] | None:
        """
        Normalize tool arguments from a provider response.

        Contract:
            - dict                         -> returned unchanged.
            - JSON object string            -> parsed into dict.
            - JSON array/primitive string   -> {"arg": <parsed>}.
            - Empty string / whitespace     -> {}.
            - None                          -> {}.
            - Plain non-JSON string         -> {"arg": "<string>"}.
            - Unsupported types (e.g., custom objects, functions) -> None (failure).

        This function never raises; it returns None to indicate conversion failure.
        """
        if args is None:
            return {}
        if isinstance(args, dict):
            return args
        if isinstance(args, str):
            stripped = args.strip()
            if not stripped:
                return {}
            try:
                parsed = json.loads(stripped)
                if isinstance(parsed, dict):
                    return parsed
                # Non-object JSON: wrap as a single argument.
                return {"arg": parsed}
            except json.JSONDecodeError:
                # Not valid JSON: treat as raw string.
                return {"arg": stripped}
        # Unsupported type
        return None

    @classmethod
    def convert_provider_tool_calls(
        cls,
        provider_calls: Sequence[ProviderToolCall],
    ) -> tuple[list[ToolCall], list[ToolResult]]:
        """
        Convert a list of provider tool calls into internal ToolCall objects.

        Returns:
            tuple: (converted_calls, conversion_errors)
                - converted_calls: list of ToolCall objects for successfully parsed calls.
                - conversion_errors: list of ToolResult objects for calls that failed conversion.
        """
        converted_calls: list[ToolCall] = []
        errors: list[ToolResult] = []

        for tc in provider_calls:
            name = tc.function.name if tc.function else ""
            args = cls.normalize_arguments(tc.function.arguments if tc.function else None)
            if args is None:
                errors.append(ToolResult(
                    call_id=tc.id,
                    status=ToolStatus.FAILED,
                    error=f"Invalid arguments for tool '{name}'",
                ))
            else:
                converted_calls.append(ToolCall(
                    id=tc.id,
                    tool_name=name,
                    arguments=args,
                    timeout=None,
                ))

        return converted_calls, errors