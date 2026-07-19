"""
===============================================================================
Plan and PlanStep
===============================================================================
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from time import time
from uuid import uuid4

from .domain import Domain

@dataclass(slots=True)
class PlanStep:
    domain: Domain          # non-default first
    instruction: str        # non-default
    id: str = field(default_factory=lambda: str(uuid4()))
    options: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass(slots=True)
class Plan:
    steps: List[PlanStep] = field(default_factory=list)
    status: str = "created"
    created_at: float = field(default_factory=time)
    version: str = "1.0"
    metadata: Dict[str, Any] = field(default_factory=dict)