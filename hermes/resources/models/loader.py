"""
===============================================================================
Hermes Runtime Model Loader
===============================================================================

Loads Runtime Models from JSON resources.

Genesis implementation currently provides only the interface.

===============================================================================
"""

from __future__ import annotations

from pathlib import Path

from .model import RuntimeModel


class ModelLoader:
    """
    Loads Runtime Models.
    """

    def load(
        self,
        directory: Path,
    ) -> list[RuntimeModel]:

        return []