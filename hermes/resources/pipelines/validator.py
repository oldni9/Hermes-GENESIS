"""
===============================================================================
Hermes Runtime Pipeline Validator

Validates Runtime Pipelines.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.resources.pipelines.pipeline import RuntimePipeline


class RuntimePipelineValidator:

    def validate(
        self,
        pipeline: RuntimePipeline,
    ) -> None:

        if not pipeline.name.strip():

            raise ValueError(
                "Pipeline name cannot be empty."
            )

        if len(pipeline.stages) == 0:

            raise ValueError(
                "Pipeline must contain at least one stage."
            )