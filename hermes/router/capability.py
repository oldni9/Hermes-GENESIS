"""
===============================================================================
Model Capability
===============================================================================
"""

from __future__ import annotations

from enum import Enum


class ModelCapability(Enum):

    CHAT = "chat"

    VISION = "vision"

    IMAGE = "image"

    AUDIO = "audio"

    EMBEDDING = "embedding"

    TOOLS = "tools"

    REASONING = "reasoning"
