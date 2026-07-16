"""
===============================================================================
Hermes AI Pipeline

Orchestrates AI execution.

Does NOT perform AI.

Does NOT know OCR, Vision, Speech, Embeddings, or Chat.

Only coordinates:
    - AIManager
    - AICache
    - AIRequest
    - AIResponse
    - AIContext

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.ai.cache import AICache
from hermes.ai.context import AIContext
from hermes.ai.manager import AIManager
from hermes.ai.request import AIRequest
from hermes.ai.response import AIResponse


class AIPipeline:
    """
    Orchestrates AI execution.

    The pipeline coordinates caching and execution.

    It does not know about specific capabilities.

    It does not know about providers.

    It only orchestrates.
    """

    def __init__(
        self,
        manager: AIManager,
        cache: AICache | None = None,
    ) -> None:
        """
        Initialize the AI pipeline.

        Parameters
        ----------
        manager : AIManager
            The AI manager to use for execution.
        cache : AICache | None, optional
            Cache instance. If None, a new cache is created.
        """

        self._manager = manager

        if cache is None:
            self._cache = AICache()
        else:
            self._cache = cache

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def manager(self) -> AIManager:
        """
        Return the underlying AI manager.
        """

        return self._manager

    @property
    def cache(self) -> AICache:
        """
        Return the underlying AI cache.
        """

        return self._cache

    # ------------------------------------------------------------------
    # Execution
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
            Time-to-live for cached response. None means never expire.

        Returns
        -------
        AIResponse
            The response from the provider or cache.

        Raises
        ------
        KeyError
            If provider does not exist.
        """

        # Check cache first
        if use_cache:
            cached = self._cache.get(request)

            if cached is not None:
                return cached

        # Execute through manager
        response = self._manager.execute(
            provider_name=provider,
            request=request,
            context=context,
        )

        # Store in cache if enabled and successful
        if use_cache and response.success:
            self._cache.store(
                request=request,
                response=response,
                ttl=cache_ttl,
            )

        return response

    # ------------------------------------------------------------------

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
            Time-to-live for cached response. None means never expire.

        Returns
        -------
        AIResponse
            The response from the provider or cache.

        Raises
        ------
        RuntimeError
            If no provider supports the capability.
        """

        # Check cache first
        if use_cache:
            cached = self._cache.get(request)

            if cached is not None:
                return cached

        # Execute through manager
        response = self._manager.execute_default(
            capability=capability,
            request=request,
            context=context,
        )

        # Store in cache if enabled and successful
        if use_cache and response.success:
            self._cache.store(
                request=request,
                response=response,
                ttl=cache_ttl,
            )

        return response

    # ------------------------------------------------------------------

    def batch_execute(
        self,
        provider: str,
        requests: list[AIRequest],
        context: AIContext | None = None,
        *,
        use_cache: bool = True,
        cache_ttl: float | None = None,
    ) -> list[AIResponse]:
        """
        Execute multiple requests using a specific provider.

        Parameters
        ----------
        provider : str
            Name of the provider to use.
        requests : list[AIRequest]
            List of requests to execute.
        context : AIContext | None, optional
            Optional execution context.
        use_cache : bool, default=True
            Whether to use the cache.
        cache_ttl : float | None, optional
            Time-to-live for cached responses. None means never expire.

        Returns
        -------
        list[AIResponse]
            List of responses from the provider or cache.

        Raises
        ------
        KeyError
            If provider does not exist.
        """

        # If cache is disabled, delegate directly to manager
        if not use_cache:
            return self._manager.batch_execute(
                provider_name=provider,
                requests=requests,
                context=context,
            )

        responses: list[AIResponse | None] = []

        # Track which requests need execution
        to_execute: list[int] = []
        executed_requests: list[AIRequest] = []

        # Check cache for each request
        for idx, request in enumerate(requests):
            cached = self._cache.get(request)

            if cached is not None:
                responses.append(cached)
            else:
                # Mark for execution
                to_execute.append(idx)
                executed_requests.append(request)
                responses.append(None)

        # Execute uncached requests in batch
        if executed_requests:
            batch_responses = self._manager.batch_execute(
                provider_name=provider,
                requests=executed_requests,
                context=context,
            )

            # Store and insert responses
            for idx, request, response in zip(
                to_execute,
                executed_requests,
                batch_responses,
            ):
                if response.success and use_cache:
                    self._cache.store(
                        request=request,
                        response=response,
                        ttl=cache_ttl,
                    )

                responses[idx] = response

        # Filter out None values (should not happen after execution)
        return [r for r in responses if r is not None]

    # ------------------------------------------------------------------
    # Cache Management
    # ------------------------------------------------------------------

    def clear_cache(self) -> None:
        """
        Remove every entry from the cache.
        """

        self._cache.clear()

    # ------------------------------------------------------------------

    def cleanup_cache(self) -> int:
        """
        Remove every expired entry from the cache.

        Returns
        -------
        int
            Number of entries removed.
        """

        return self._cache.cleanup()

    # ------------------------------------------------------------------

    def cache_size(self) -> int:
        """
        Return the number of valid (non-expired) cache entries.

        Returns
        -------
        int
            Number of valid cache entries.
        """

        return self._cache.count()

    # ------------------------------------------------------------------
    # Magic Methods
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        """
        Return the number of valid cache entries.
        """

        return self._cache.count()