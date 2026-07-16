"""
===============================================================================
Hermes Knowledge Context
===============================================================================
"""

from __future__ import annotations


class KnowledgeContext:
    """
    Shared context for knowledge operations.
    """

    def __init__(self):

        self._values: dict[str, object] = {}

    def set(self, key: str, value):

        self._values[key] = value

    def get(self, key: str, default=None):

        return self._values.get(key, default)

    def remove(self, key: str):

        self._values.pop(key, None)

    def clear(self):

        self._values.clear()

    @property
    def values(self):

        return dict(self._values)