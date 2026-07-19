"""
===============================================================================
Hermes Runtime Provider Telemetry

Collects runtime statistics.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from collections import defaultdict


class ProviderTelemetry:

    def __init__(self) -> None:

        self._requests = defaultdict(int)

        self._successes = defaultdict(int)

        self._failures = defaultdict(int)

        self._latencies = defaultdict(list)

    # --------------------------------------------------------------

    def record_request(
        self,
        provider: str,
    ) -> None:

        self._requests[provider] += 1

    # --------------------------------------------------------------

    def record_success(
        self,
        provider: str,
    ) -> None:

        self._successes[provider] += 1

    # --------------------------------------------------------------

    def record_failure(
        self,
        provider: str,
    ) -> None:

        self._failures[provider] += 1

    # --------------------------------------------------------------

    def record_latency(
        self,
        provider: str,
        latency: float,
    ) -> None:

        self._latencies[provider].append(latency)

    # --------------------------------------------------------------

    def summary(
        self,
        provider: str,
    ) -> dict:

        return {
            "requests": self._requests[provider],
            "successes": self._successes[provider],
            "failures": self._failures[provider],
            "latencies": self._latencies[provider],
        }
