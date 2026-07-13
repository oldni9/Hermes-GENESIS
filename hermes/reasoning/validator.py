"""
===============================================================================
Hermes Reasoning Validator

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.reasoning.execution_graph import ExecutionGraph


class ReasoningValidator:

    def validate(
        self,
        graph: ExecutionGraph,
    ) -> None:

        if not graph.nodes:

            raise ValueError(
                "Execution graph contains no nodes."
            )