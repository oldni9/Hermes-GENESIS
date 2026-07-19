"""
===============================================================================
Planner
===============================================================================
"""
from __future__ import annotations
import json
from typing import Optional

from .backend import PlanningBackend
from .domain import Domain
from .plan import Plan, PlanStep
from .exceptions import PlanningError

class Planner:
    """
    The Planner converts a user prompt into a Plan of Domains.
    Uses a PlanningBackend to classify or generate plans.
    """
    def __init__(self, backend: PlanningBackend, default_domain: Domain = Domain.GENERAL):
        self._backend = backend
        self._default_domain = default_domain

    def plan(self, prompt: str) -> Plan:
        """Plan a user request."""
        if not prompt or not prompt.strip():
            raise PlanningError("Prompt cannot be empty")

        # Attempt multi-step planning if the backend supports it
        try:
            plan_json = self._backend.generate_plan(prompt)
            return self._parse_plan_json(plan_json)
        except NotImplementedError:
            # Backend explicitly says generation is not supported – fall back to classification
            pass
        # Any other exception (including PlanningError) propagates

        # Fallback to single-step classification
        domain_name = self._backend.classify(prompt)
        try:
            domain = Domain(domain_name)
        except ValueError:
            domain = self._default_domain

        step = PlanStep(domain=domain, instruction=prompt)
        return Plan(steps=[step])

    def _parse_plan_json(self, plan_json: str) -> Plan:
        """
        Parse a JSON string into a Plan.
        Expected format: list of objects with fields:
            id (optional, default auto-generated)
            domain (string)
            instruction (string)
            depends_on (list of strings, optional)
        """
        try:
            data = json.loads(plan_json)
        except json.JSONDecodeError as e:
            raise PlanningError(f"Failed to parse plan JSON: {e}")

        if not isinstance(data, list):
            raise PlanningError("Plan JSON must be a list of steps")

        steps: list[PlanStep] = []
        for item in data:
            if not isinstance(item, dict):
                raise PlanningError("Each step must be a dict")
            domain_str = item.get("domain")
            if not domain_str:
                raise PlanningError("Missing 'domain' in step")
            try:
                domain = Domain(domain_str)
            except ValueError:
                raise PlanningError(f"Invalid domain '{domain_str}'")
            instruction = item.get("instruction")
            if not instruction:
                raise PlanningError("Missing 'instruction' in step")
            depends_on = item.get("depends_on")
            if depends_on is not None and not isinstance(depends_on, list):
                raise PlanningError("'depends_on' must be a list")
            step_id = item.get("id")
            # Build PlanStep with explicit ID if provided
            step = PlanStep(
                domain=domain,
                instruction=instruction,
                depends_on=depends_on or [],
                id=step_id,
            )
            steps.append(step)

        return Plan(steps=steps)