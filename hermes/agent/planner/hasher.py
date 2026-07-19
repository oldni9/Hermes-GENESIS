"""
===============================================================================
Tool Call Hasher
===============================================================================

Dependencies:
    - hashlib
    - json
    - hermes.ai.response

Consumes:
    - ToolCall

Produces:
    - ToolCallHasher

Public API:
    - ToolCallHasher
===============================================================================
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from hermes.ai.response import ToolCall


class ToolCallHasher:
    """
    Provides deterministic hashing for ToolCalls based on tool name and arguments.
    """

    @staticmethod
    def _normalize_arguments(args: Any) -> Any:
        """Normalize arguments to a consistent JSON-serializable format."""
        if args is None:
            return {}
        if isinstance(args, str):
            try:
                parsed = json.loads(args)
                return parsed if isinstance(parsed, dict) else {"_raw": args}
            except json.JSONDecodeError:
                return {"_raw": args}
        return args

    @staticmethod
    def fingerprint(call: ToolCall) -> str:
        """
        Generate a SHA-256 fingerprint for a ToolCall.
        """
        name = call.function.name if call.function else "unknown"
        args = ToolCallHasher._normalize_arguments(call.function.arguments if call.function else None)
        
        normalized = json.dumps(
            {"name": name, "args": args},
            sort_keys=True,
            default=str
        )
        
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()