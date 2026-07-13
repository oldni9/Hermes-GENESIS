"""
===============================================================================
Hermes Provider Types
===============================================================================
"""

from __future__ import annotations

from enum import Enum


class ProviderType(str, Enum):

    LOCAL = "local"

    OPENROUTER = "openrouter"

    GROQ = "groq"

    CEREBRAS = "cerebras"

    ZAI = "zai"

    CLOUDFLARE = "cloudflare"

    MISTRAL = "mistral"

    CUSTOM = "custom"