"""
===============================================================================
Planning Backend – abstraction over the execution pipeline
===============================================================================
"""
from __future__ import annotations
from typing import Protocol, Optional, runtime_checkable

from hermes.ai.pipeline import AIPipeline
from hermes.ai.request import AIRequest
from hermes.planning.prompts import CLASSIFIER_SYSTEM_PROMPT, PLAN_GENERATION_SYSTEM_PROMPT
from hermes.planning.config import PlanningConfig
from hermes.planning.exceptions import PlanningError

@runtime_checkable
class PlanningBackend(Protocol):
    """Protocol for any planning backend."""
    def classify(self, prompt: str) -> str:
        """Return the domain name (as a string) for the given prompt."""
        ...

    def generate_plan(self, prompt: str) -> str:
        """
        Return a JSON string representing a multi-step plan.
        The JSON should be a list of steps, each with:
            - domain: str
            - instruction: str
            - depends_on: list[str] (optional)
        If the backend does not support plan generation, it SHOULD raise NotImplementedError.
        """
        ...

class PipelinePlanningBackend:
    """Planning backend that uses the Hermes Pipeline."""
    def __init__(self, pipeline: AIPipeline, config: PlanningConfig | None = None):
        self._pipeline = pipeline
        self._config = config or PlanningConfig()

    def classify(self, prompt: str) -> str:
        if not prompt or not prompt.strip():
            raise PlanningError("Prompt cannot be empty")

        request = AIRequest(
            prompt=prompt,
            task="chat",
            options={
                "messages": [
                    {"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ]
            },
        )
        if self._config.planner_provider:
            request.provider = self._config.planner_provider
        if self._config.planner_model:
            request.model = self._config.planner_model

        try:
            response = self._pipeline.execute(
                provider=request.provider or None,
                request=request,
            )
        except Exception as exc:
            raise PlanningError(f"Classification failed: {exc}") from exc

        if not response.success:
            raise PlanningError(f"Classification failed: {response.message}")

        domain = response.text().strip().lower()
        if not domain:
            raise PlanningError("Classification failed: Empty response")

        return domain

    def generate_plan(self, prompt: str) -> str:
        """
        Generate a multi-step plan in JSON format.
        """
        if not prompt or not prompt.strip():
            raise PlanningError("Prompt cannot be empty")

        request = AIRequest(
            prompt=prompt,
            task="chat",
            options={
                "messages": [
                    {"role": "system", "content": PLAN_GENERATION_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ]
            },
        )
        if self._config.planner_provider:
            request.provider = self._config.planner_provider
        if self._config.planner_model:
            request.model = self._config.planner_model

        try:
            response = self._pipeline.execute(
                provider=request.provider or None,
                request=request,
            )
        except Exception as exc:
            raise PlanningError(f"Plan generation failed: {exc}") from exc

        if not response.success:
            raise PlanningError(f"Plan generation failed: {response.message}")

        plan_json = response.text().strip()
        if not plan_json:
            raise PlanningError("Plan generation failed: Empty response")

        return plan_json