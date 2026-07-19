"""
===============================================================================
Hermes AI Pipeline

Orchestrates AI execution.

Now delegates to AIOrchestrator and supports middleware.

Does NOT perform AI.
Does NOT know OCR, Vision, Speech, Embeddings, or Chat.
Only coordinates:
    - AICache
    - AIOrchestrator
    - Middleware
    - AIRequest
    - AIResponse
    - AIContext

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from typing import Generator, List

from hermes.ai.cache import AICache
from hermes.ai.context import AIContext
from hermes.ai.orchestrator import AIOrchestrator, ExecutionPlan
from hermes.ai.request import AIRequest
from hermes.ai.response import AIResponse, ResponseChunk
from hermes.ai.middleware import (
    BaseMiddleware,
    MiddlewareChain,
    MiddlewareContext,
    MiddlewareShortCircuit,
)


class AIPipeline:
    """
    Orchestrates AI execution.

    The pipeline coordinates caching, middleware, and orchestration.

    It does not know about specific capabilities.

    It does not know about providers.

    It only orchestrates.
    """

    def __init__(
        self,
        orchestrator: AIOrchestrator,
        cache: AICache | None = None,
        middlewares: List[BaseMiddleware] | None = None,
    ) -> None:
        """
        Initialize the AI pipeline.

        Parameters
        ----------
        orchestrator : AIOrchestrator
            The orchestrator for execution.
        cache : AICache | None, optional
            Cache instance. If None, a new cache is created.
        middlewares : List[BaseMiddleware] | None, optional
            List of middleware to apply to every request.
        """
        self._orchestrator = orchestrator
        self._cache = cache or AICache()
        self._middleware_chain = MiddlewareChain(middlewares)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def orchestrator(self) -> AIOrchestrator:
        """Return the underlying orchestrator."""
        return self._orchestrator

    @property
    def cache(self) -> AICache:
        """Return the underlying cache."""
        return self._cache

    @property
    def middleware_chain(self) -> MiddlewareChain:
        """Return the middleware chain."""
        return self._middleware_chain

    def add_middleware(self, middleware: BaseMiddleware) -> None:
        """
        Add a middleware to the chain.

        Parameters
        ----------
        middleware : BaseMiddleware
            The middleware to add.
        """
        self._middleware_chain.add(middleware)

    # ------------------------------------------------------------------
    # Internal execution (shared by execute and execute_default)
    # ------------------------------------------------------------------

    def _execute_with_middleware(
        self,
        provider: str | None,
        request: AIRequest,
        context: AIContext | None = None,
        *,
        use_cache: bool = True,
        cache_ttl: float | None = None,
    ) -> AIResponse:
        """
        Internal execution that applies cache, middleware, and orchestration.

        This is the common path for both execute() and execute_default().
        """
        # 1. Cache lookup
        if use_cache:
            cached = self._cache.get(request)
            if cached is not None:
                return cached

        # 2. Build middleware context
        ctx = MiddlewareContext(
            request=request,
            context=context,
            metadata={},
        )

        # 3. Execute before hooks
        try:
            self._middleware_chain.execute_before(ctx)
        except MiddlewareShortCircuit:
            if ctx.response is None:
                raise RuntimeError(
                    "Middleware short‑circuited but no response was set."
                )
            return ctx.response

        # Use possibly modified request
        request = ctx.request

        # 4. Build execution plan
        plan = ExecutionPlan(
            provider=provider,
            use_cache=use_cache,
            cache_ttl=cache_ttl,
        )

        # 5. Execute via orchestrator
        response = self._orchestrator.execute(
            request=request,
            plan=plan,
            context=context,
        )

        # 6. Store response in context for after hooks
        ctx.response = response

        # 7. Execute after hooks
        self._middleware_chain.execute_after(ctx)

        # 8. Use possibly modified response
        response = ctx.response

        # 9. Store in cache
        if use_cache and response.success:
            self._cache.store(request, response, ttl=cache_ttl)

        return response

    # ------------------------------------------------------------------
    # Public execution methods
    # ------------------------------------------------------------------

    def execute(
        self,
        provider: str,
        request: AIRequest,
        context: AIContext | None = None,
        *,
        use_cache: bool = True,
        cache_ttl: float | None = None,
    ) -> AIResponse:
        """
        Execute a request using a specific provider.

        Parameters
        ----------
        provider : str
            Name of the provider to use.
        request : AIRequest
            The request to execute.
        context : AIContext | None, optional
            Optional execution context.
        use_cache : bool, default=True
            Whether to use the cache.
        cache_ttl : float | None, optional
            Time-to-live for cached response.

        Returns
        -------
        AIResponse
            The response from the provider or cache.

        Raises
        ------
        KeyError
            If provider does not exist.
        """
        return self._execute_with_middleware(
            provider=provider,
            request=request,
            context=context,
            use_cache=use_cache,
            cache_ttl=cache_ttl,
        )

    def execute_default(
        self,
        capability: str,
        request: AIRequest,
        context: AIContext | None = None,
        *,
        use_cache: bool = True,
        cache_ttl: float | None = None,
    ) -> AIResponse:
        """
        Execute a request using the default provider for the capability.

        Parameters
        ----------
        capability : str
            Capability required.
        request : AIRequest
            The request to execute.
        context : AIContext | None, optional
            Optional execution context.
        use_cache : bool, default=True
            Whether to use the cache.
        cache_ttl : float | None, optional
            Time-to-live for cached response.

        Returns
        -------
        AIResponse
            The response from the provider or cache.

        Raises
        ------
        RuntimeError
            If no provider supports the capability.
        """
        # Set task if not already set
        if not request.task:
            request.task = capability

        return self._execute_with_middleware(
            provider=None,  # orchestrator will select default provider
            request=request,
            context=context,
            use_cache=use_cache,
            cache_ttl=cache_ttl,
        )

    # ------------------------------------------------------------------
    # Streaming (unchanged – will be enhanced in a later PR)
    # ------------------------------------------------------------------

    def stream(
        self,
        provider: str,
        request: AIRequest,
        context: AIContext | None = None,
        *,
        use_cache: bool = False,
        cache_ttl: float | None = None,
    ) -> Generator[ResponseChunk, None, AIResponse]:
        """
        Execute a request with streaming using a specific provider.

        Parameters
        ----------
        provider : str
            Name of the provider to use.
        request : AIRequest
            The request to execute.
        context : AIContext | None, optional
            Optional execution context.
        use_cache : bool, default=False
            Whether to use the cache (not recommended for streaming).
        cache_ttl : float | None, optional
            Time-to-live for cached response.

        Yields
        ------
        ResponseChunk
            Partial response chunks.

        Returns
        -------
        AIResponse
            The final assembled response.
        """
        # For now, we bypass middleware and cache for streaming.
        # This will be enhanced in a future PR.
        plan = ExecutionPlan(
            provider=provider,
            use_cache=False,
            cache_ttl=cache_ttl,
        )

        final_response = yield from self._orchestrator.stream(
            request=request,
            plan=plan,
            context=context,
        )

        if use_cache and final_response.success:
            self._cache.store(request, final_response, ttl=cache_ttl)

        return final_response

    # ------------------------------------------------------------------
    # Cache Management
    # ------------------------------------------------------------------

    def clear_cache(self) -> None:
        """Remove every entry from the cache."""
        self._cache.clear()

    def cleanup_cache(self) -> int:
        """Remove every expired entry from the cache."""
        return self._cache.cleanup()

    def cache_size(self) -> int:
        """Return the number of valid (non-expired) cache entries."""
        return self._cache.count()

    # ------------------------------------------------------------------
    # Magic Methods
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        """Return the number of valid cache entries."""
        return self._cache.count()
