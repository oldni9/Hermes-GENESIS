"""
===============================================================================
Hermes Runtime Pipeline Selector

Selects execution pipelines.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.resources.pipelines.pipeline import RuntimePipeline


class RuntimePipelineSelector:

    def select(
        self,
        pipelines: list[RuntimePipeline],
    ) -> RuntimePipeline | None:

        if not pipelines:
            return None

        pipelines.sort(
            key=lambda pipeline: pipeline.priority,
            reverse=True,
        )

        return pipelines[0]