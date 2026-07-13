"""
===============================================================================
Hermes Runtime Model Ranking

Ranks Runtime Models using the score engine.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from hermes.resources.models.model import RuntimeModel
from hermes.resources.models.score import ModelScoreEngine


class ModelRanking:
    """
    Sort Runtime Models by score.
    """

    def __init__(self) -> None:

        self._score = ModelScoreEngine()

    # ------------------------------------------------------------------

    def rank(
        self,
        models: list[RuntimeModel],
    ) -> list[RuntimeModel]:

        return sorted(
            models,
            key=self._score.score,
            reverse=True,
        )

    # ------------------------------------------------------------------

    def best(
        self,
        models: list[RuntimeModel],
    ) -> RuntimeModel | None:

        ranked = self.rank(models)

        if not ranked:
            return None

        return ranked[0]