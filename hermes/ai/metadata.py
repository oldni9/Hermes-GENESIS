"""
===============================================================================
Hermes AI Metadata

Describes an AI provider.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class AIMetadata:
    """
    Metadata describing an AI provider.
    """

    name: str

    version: str = "1.0"

    author: str = "Aryan"

    description: str = ""

    provider: str = ""

    category: str = ""

    capabilities: list[str] = field(
        default_factory=list,
    )

    supported_inputs: list[str] = field(
        default_factory=list,
    )

    supported_outputs: list[str] = field(
        default_factory=list,
    )

    models: list[str] = field(
        default_factory=list,
    )

    enabled: bool = True

    # -------------------------------------------------------------

    def supports(
        self,
        capability: str,
    ) -> bool:

        return capability in self.capabilities

    # -------------------------------------------------------------

    def add_capability(
        self,
        capability: str,
    ) -> None:

        if capability not in self.capabilities:

            self.capabilities.append(capability)

    # -------------------------------------------------------------

    def remove_capability(
        self,
        capability: str,
    ) -> None:

        if capability in self.capabilities:

            self.capabilities.remove(capability)
