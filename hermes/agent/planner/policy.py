"""
===============================================================================
Planner Policy
===============================================================================

Dependencies:
    - dataclasses

Consumes:
    - None

Produces:
    - PlannerPolicy

Public API:
    - PlannerPolicy
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PlannerPolicy:
    """
    Configuration policy for the ReasoningPlanner.
    """
    minimum_response_length: int = 10
    retry_on_empty: bool = True
    retry_on_low_confidence: bool = True
    max_retries_on_failure: int = 2
    abort_on_repeated_failure: bool = True
    min_confidence_threshold: float = 0.5  # FIX: Moved magic number to policy