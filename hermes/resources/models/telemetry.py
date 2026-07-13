"""
===============================================================================
Hermes Runtime Model Telemetry

Collects runtime statistics for models.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from collections import defaultdict
from time import time


class ModelTelemetry:
    """
    Collects runtime statistics.

    Telemetry is session-based.

    Long-term persistence belongs to History.
    """

    def __init__(self) -> None:

        self._requests = defaultdict(int)

        self._successes = defaultdict(int)

        self._failures = defaultdict(int)

        self._latency = defaultdict(list)

        self._cost = defaultdict(list)

    # ------------------------------------------------------------------

    def record_request(
        self,
        model: str,
    ) -> None:

        self._requests[model] += 1

    # ------------------------------------------------------------------

    def record_success(
        self,
        model: str,
    ) -> None:

        self._successes[model] += 1

    # ------------------------------------------------------------------

    def record_failure(
        self,
        model: str,
    ) -> None:

        self._failures[model] += 1

    # ------------------------------------------------------------------

    def record_latency(
        self,
        model: str,
        latency: float,
    ) -> None:

        self._latency[model].append(latency)

    # ------------------------------------------------------------------

    def record_cost(
        self,
        model: str,
        cost: float,
    ) -> None:

        self._cost[model].append(cost)

    # ------------------------------------------------------------------

    def summary(
        self,
        model: str,
    ) -> dict:

        return {
            "requests": self._requests[model],
            "successes": self._successes[model],
            "failures": self._failures[model],
            "latency": self._latency[model],
            "cost": self._cost[model],
            "timestamp": time(),
        }