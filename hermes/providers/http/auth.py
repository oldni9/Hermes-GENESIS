"""
===============================================================================
Hermes Authentication Strategies
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AuthStrategy:

    api_key: str | None = None

    header: str = "Authorization"

    prefix: str = "Bearer"

    def headers(self) -> dict[str, str]:

        if not self.api_key:
            return {}

        return {
            self.header: f"{self.prefix} {self.api_key}"
        }