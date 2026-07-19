"""
===============================================================================
Hermes Runtime Pipeline Registry

Stores Runtime Pipelines.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.resources.pipelines.pipeline import RuntimePipeline


class RuntimePipelineRegistry:

    def __init__(self) -> None:

        self._pipelines: dict[str, RuntimePipeline] = {}

    # --------------------------------------------------------------

    def register(
        self,
        pipeline: RuntimePipeline,
    ) -> None:

        self._pipelines[pipeline.name] = pipeline

    # --------------------------------------------------------------

    def get(
        self,
        name: str,
    ) -> RuntimePipeline | None:

        return self._pipelines.get(name)

    # --------------------------------------------------------------

    def all(
        self,
    ) -> list[RuntimePipeline]:

        return list(self._pipelines.values())

    # --------------------------------------------------------------

    def enabled(
        self,
    ) -> list[RuntimePipeline]:

        return [pipeline for pipeline in self._pipelines.values() if pipeline.enabled]
