"""
===============================================================================
Hermes Runtime Pipeline Profile

Pipeline execution profile.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RuntimePipelineProfile:

    name: str

    pipeline: str

    enabled: bool = True
