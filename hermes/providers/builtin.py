"""
===============================================================================
Hermes Built-in Provider

Default provider used by Hermes Genesis.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from typing import Any

from hermes.providers.provider import Provider
from hermes.providers.result import ProviderResult


class BuiltinProvider(Provider):
    """
    Default built-in provider.
    """

    def __init__(self) -> None:
        super().__init__(name="general")

    def generate(
        self,
        payload: Any,
    ) -> ProviderResult:
        print("[BuiltinProvider] generate() called")
        print("[BuiltinProvider] payload =", payload)

        return ProviderResult(
            success=True,
            data=payload,
            error=None,
        )
