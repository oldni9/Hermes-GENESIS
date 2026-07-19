"""
===============================================================================
Hermes AI Middleware

Middleware system for the AI Pipeline.

Middleware components can inspect, modify, or short‑circuit requests and
responses as they flow through the pipeline.

Execution order:
    Cache check (if enabled)
    ↓
    Middleware.before()  (in registration order)
    ↓
    Orchestrator.execute()
    ↓
    Middleware.after()   (in reverse registration order)
    ↓
    Cache store (if enabled)
    ↓
    Return response

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, List, Optional

from hermes.ai.request import AIRequest
from hermes.ai.response import AIResponse
from hermes.ai.context import AIContext


class MiddlewareError(Exception):
    """Base exception for all middleware-related errors."""


class MiddlewareShortCircuit(Exception):
    """
    Raised to short‑circuit the middleware chain.

    When caught, the pipeline will skip the orchestrator and return
    the response currently stored in the MiddlewareContext (if any).
    """


@dataclass(slots=True)
class MiddlewareContext:
    """
    Context passed to each middleware during execution.

    Attributes
    ----------
    request : AIRequest
        The request being processed.
    response : AIResponse | None
        The current response (set after orchestration, or by middleware
        for short‑circuit).
    context : AIContext | None
        The execution context.
    metadata : dict[str, Any]
        Arbitrary metadata for middleware to share.
    short_circuit : bool
        If set to True by a middleware, the chain will be interrupted
        and the current response will be returned (if set).
    """

    request: AIRequest
    response: Optional[AIResponse] = None
    context: Optional[AIContext] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    short_circuit: bool = False


class BaseMiddleware(ABC):
    """
    Abstract base class for all middleware.

    Middleware can be executed before and/or after the orchestrator.
    """

    @abstractmethod
    def before(self, ctx: MiddlewareContext) -> None:
        """
        Called before the orchestrator executes the request.

        Can modify the request, set ctx.short_circuit to bypass the
        orchestrator, or raise an exception.

        Parameters
        ----------
        ctx : MiddlewareContext
            The context containing the request and metadata.
        """
        ...

    @abstractmethod
    def after(self, ctx: MiddlewareContext) -> None:
        """
        Called after the orchestrator has executed the request.

        Can modify the response, add metadata, or raise an exception.

        Parameters
        ----------
        ctx : MiddlewareContext
            The context containing the request, response, and metadata.
        """
        ...


class MiddlewareChain:
    """
    Manages a list of middleware and executes them in order.

    Before hooks are executed in registration order.
    After hooks are executed in reverse registration order.
    """

    def __init__(self, middlewares: Optional[List[BaseMiddleware]] = None) -> None:
        """
        Initialize the chain with an optional list of middleware.

        Parameters
        ----------
        middlewares : list[BaseMiddleware] | None, optional
            Initial middleware list.
        """
        self._middlewares: list[BaseMiddleware] = (
            list(middlewares) if middlewares else []
        )

    def add(self, middleware: BaseMiddleware) -> None:
        """
        Add a middleware to the end of the chain.

        Parameters
        ----------
        middleware : BaseMiddleware
            The middleware to add.
        """
        self._middlewares.append(middleware)

    def execute_before(self, ctx: MiddlewareContext) -> None:
        """
        Execute all before hooks in registration order.

        If a middleware sets ctx.short_circuit to True, a
        MiddlewareShortCircuit exception is raised to stop further
        processing.

        Parameters
        ----------
        ctx : MiddlewareContext
            The context to pass to each middleware.

        Raises
        ------
        MiddlewareShortCircuit
            When a middleware short‑circuits the chain.
        """
        for mw in self._middlewares:
            mw.before(ctx)
            if ctx.short_circuit:
                raise MiddlewareShortCircuit(
                    f"Short‑circuited by middleware {mw.__class__.__name__}"
                )

    def execute_after(self, ctx: MiddlewareContext) -> None:
        """
        Execute all after hooks in reverse registration order.

        Parameters
        ----------
        ctx : MiddlewareContext
            The context to pass to each middleware.

        Raises
        ------
        Exception
            Any exception raised by a middleware after hook.
        """
        for mw in reversed(self._middlewares):
            mw.after(ctx)

    def __len__(self) -> int:
        """Return the number of middleware in the chain."""
        return len(self._middlewares)

    def __bool__(self) -> bool:
        """Return True if the chain contains at least one middleware."""
        return bool(self._middlewares)
