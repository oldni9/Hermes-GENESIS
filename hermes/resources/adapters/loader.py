"""
===============================================================================
Hermes Adapter Loader
===============================================================================

Loads Runtime Adapter Objects from JSON resources.

Current Genesis implementation only defines the interface.

JSON loading will be implemented once Runtime Objects are finalized.

===============================================================================
"""

from __future__ import annotations

from pathlib import Path

from .adapter import RuntimeAdapter


class AdapterLoader:
    """
    Loads Runtime Adapter Objects.
    """

    def load(
        self,
        directory: Path,
    ) -> list[RuntimeAdapter]:
        """
        Load adapters from a directory.

        Genesis implementation returns an empty list.
        """

        return []
