"""
===============================================================================
Hermes Capability Types
===============================================================================
"""

from __future__ import annotations

from enum import Enum


class CapabilityType(str, Enum):

    CHAT = "chat"

    VISION = "vision"

    CODE = "code"

    REASONING = "reasoning"

    EMBEDDING = "embedding"

    IMAGE = "image"

    AUDIO = "audio"

    WEB = "web"

    TOOLS = "tools"

    MEMORY = "memory"
