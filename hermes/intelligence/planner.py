"""
===============================================================================
Hermes Planner
===============================================================================
"""

from __future__ import annotations

from hermes.intelligence.intent import Intent
from hermes.intelligence.plan import ExecutionPlan


class Planner:

    def create_plan(
        self,
        intent: Intent,
    ) -> ExecutionPlan:

        plan = ExecutionPlan(
            intent=intent,
        )

        plan.add_step("process_request")

        return plan
