"""
===============================================================================
Hermes AI Retry Policy

Exponential backoff retry policy for AI execution.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Callable, Type

from hermes.ai.orchestrator.constants import MAX_RETRY_ATTEMPTS
from hermes.ai.orchestrator.exceptions import RetryExhaustedError


@dataclass(slots=True)
class RetryPolicy:
    """
    Exponential backoff retry policy.

    Supports:
        - Exponential backoff with jitter
        - Configurable max attempts
        - Configurable delay limits
        - Retryable exception types
    """

    max_attempts: int = MAX_RETRY_ATTEMPTS
    initial_delay: float = 1.0
    max_delay: float = 30.0
    backoff_factor: float = 2.0
    retryable_exceptions: tuple[Type[Exception], ...] = ()
    should_retry: Callable[[Exception], bool] | None = None

    def execute(
        self,
        func: Callable,
        *args,
        **kwargs,
    ) -> tuple[object, int, float]:
        """
        Execute a function with retries.

        Returns (result, attempt_count, total_time_seconds).

        Raises
        ------
        RetryExhaustedError
            If all retry attempts are exhausted. Includes the last error.
        """
        last_error: Exception | None = None
        delay = self.initial_delay
        start_time = time.time()

        for attempt in range(self.max_attempts):
            try:
                result = func(*args, **kwargs)
                total_time = time.time() - start_time
                return result, attempt + 1, total_time
            except Exception as e:
                last_error = e

                # Check if exception is retryable
                if self.should_retry is not None:
                    if not self.should_retry(e):
                        raise
                elif self.retryable_exceptions:
                    if not isinstance(e, self.retryable_exceptions):
                        raise

                if attempt == self.max_attempts - 1:
                    break

                # Exponential backoff with jitter (10% variation)
                sleep_time = min(delay, self.max_delay)
                sleep_time = sleep_time * random.uniform(0.9, 1.1)
                time.sleep(sleep_time)
                delay *= self.backoff_factor

        raise RetryExhaustedError(
            f"All {self.max_attempts} retry attempts exhausted. "
            f"Last error: {last_error}"
        ) from last_error

    @classmethod
    def default(cls) -> RetryPolicy:
        """Default retry policy for AI execution."""
        return cls(
            max_attempts=3,
            initial_delay=1.0,
            max_delay=30.0,
            backoff_factor=2.0,
        )
