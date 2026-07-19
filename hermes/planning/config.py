"""
===============================================================================
Planning Configuration
===============================================================================
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

@dataclass(slots=True)
class PlanningConfig:
    planner_provider: Optional[str] = None
    planner_model: Optional[str] = None
    default_domain: str = "general"
    timeout: float = 30.0
    retries: int = 2