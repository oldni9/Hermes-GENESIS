"""
===============================================================================
Agent Executor Protocols
===============================================================================

Dependencies:
    - typing
    - hermes.ai.request
    - hermes.ai.response

Consumes:
    - AIRequest

Produces:
    - PipelineProtocol

Public API:
    - PipelineProtocol
===============================================================================
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from hermes.ai.request import AIRequest
from hermes.ai.response import AIResponse


@runtime_checkable
class PipelineProtocol(Protocol):
    """
    Protocol for pipelines that can execute AI requests.
    This decouples the AgentExecutor from the concrete AIPipeline implementation.
    """

    def execute(
        self,
        provider: str,
        request: AIRequest,
        context: Any = None,
        *,
        use_cache: bool = True,
        cache_ttl: float | None = None,
    ) -> AIResponse:
        ...