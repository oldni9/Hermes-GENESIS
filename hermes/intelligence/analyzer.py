"""
===============================================================================
Hermes Analyzer
===============================================================================

Analyzes requests before planning.

===============================================================================
"""

from __future__ import annotations

from hermes.intelligence.intent import Intent
from hermes.intelligence.request import Request


class Analyzer:

    def analyze(
        self,
        request: Request,
    ) -> Intent:

        text = request.text.strip()

        if not text:

            return Intent(
                name="empty",
                confidence=1.0,
            )

        return Intent(
            name="general",
            confidence=1.0,
        )