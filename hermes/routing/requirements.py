"""
===============================================================================
Hermes Requirement Analyzer

Determines what a request actually needs before routing.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RoutingRequirements:
    """
    High-level requirements extracted from a request.
    """

    reasoning: bool = False

    vision: bool = False

    embeddings: bool = False

    image_generation: bool = False

    audio: bool = False

    live: bool = False

    coding: bool = False

    long_context: bool = False

    preferred_model: str | None = None

    preferred_provider: str | None = None


class RequirementAnalyzer:
    """
    Converts user intent into routing requirements.

    For now this is intentionally simple.

    Later this class will inspect:

    - ProviderRequest
    - Attachments
    - Images
    - Audio
    - Context size
    - User preferences
    - Runtime policies
    """

    def analyze(self) -> RoutingRequirements:
        """
        Produce an empty requirement profile.

        Future versions will inspect ProviderRequest.
        """

        return RoutingRequirements()
