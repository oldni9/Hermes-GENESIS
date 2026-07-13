"""
===============================================================================
Hermes Intent
===============================================================================

Represents the detected intent of a request.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Intent:

    name: str

    confidence: float = 1.0