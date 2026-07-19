"""
===============================================================================
Hermes Files Subsystem State
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class FilesState:

    loaded: bool = False

    workspace: str = ""

    current_directory: str = ""

    last_operation: str = ""

    last_error: str = ""
