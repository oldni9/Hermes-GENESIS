"""
===============================================================================
Hermes Runtime Model Profile

Runtime statistics attached to each model.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RuntimeModelProfile:
    """
    Dynamic runtime information.

    Unlike RuntimeModel, these values
    change while Hermes is running.
    """

    total_requests: int = 0

    successful_requests: int = 0

    failed_requests: int = 0

    average_latency: float = 0.0

    average_cost: float = 0.0

    trust_score: float = 1.0

    health_score: float = 1.0