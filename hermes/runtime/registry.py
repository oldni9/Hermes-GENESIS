"""
===============================================================================
Hermes Runtime Registry
===============================================================================
"""

from __future__ import annotations


class RuntimeRegistry:
    """
    Registry of loaded runtime subsystems.
    """

    def __init__(self) -> None:

        self._items: dict[str, object] = {}

    def register(
        self,
        name: str,
        subsystem: object,
    ) -> None:

        self._items[name.lower()] = subsystem

    def unregister(
        self,
        name: str,
    ) -> None:

        self._items.pop(name.lower(), None)

    def get(
        self,
        name: str,
    ):

        return self._items.get(name.lower())

    def exists(
        self,
        name: str,
    ) -> bool:

        return name.lower() in self._items

    def names(self):

        return sorted(self._items.keys())

    def clear(self):

        self._items.clear()

    def __len__(self):

        return len(self._items)
