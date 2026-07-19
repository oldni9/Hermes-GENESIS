"""
===============================================================================
Planning Domains
===============================================================================
"""
from __future__ import annotations
from enum import Enum

class Domain(str, Enum):
    # Ordered by abstraction level (future reasoning may wrap others)
    GENERAL = "general"
    REASONING = "reasoning"
    CHAT = "chat"
    CODE = "code"
    SEARCH = "search"
    SUMMARIZE = "summarize"
    TRANSLATE = "translate"