"""
===============================================================================
Hermes Runtime Provider Profile

Runtime statistics for Providers.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RuntimeProviderProfile:
    """
    Dynamic provider statistics.
    """

    requests: int = 0

    successes: int = 0

    failures: int = 0

    average_latency: float = 0.0

    health_score: float = 1.0

    trust_score: float = 1.0