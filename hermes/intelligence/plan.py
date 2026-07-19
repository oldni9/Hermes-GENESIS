"""
===============================================================================
Hermes Execution Plan
===============================================================================

Execution plans are produced by Intelligence and consumed by Execution.

===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field

from hermes.intelligence.intent import Intent


@dataclass(slots=True)
class ExecutionPlan:

    intent: Intent

    steps: list[str] = field(default_factory=list)

    metadata: dict = field(default_factory=dict)

    def add_step(
        self,
        step: str,
    ) -> None:

        self.steps.append(step)
