from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional
from hermes.ai.tool import Tool, ToolParameter, ParameterType, ToolStatus

@dataclass(frozen=True)
class ToolExecutionResult:
    success: bool
    output: Any
    error: Optional[str]
    duration: float
    tool_name: str
    execution_id: Optional[str] = None