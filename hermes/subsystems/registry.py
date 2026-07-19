"""
===============================================================================
Hermes Subsystem Registry
===============================================================================
"""

from __future__ import annotations

from hermes.subsystems.base import BaseSubsystem


class SubsystemRegistry:

    def __init__(self):

        self._items: dict[str, BaseSubsystem] = {}

    def register(
        self,
        subsystem: BaseSubsystem,
    ):

        self._items[subsystem.name.lower()] = subsystem

    def unregister(
        self,
        name: str,
    ):

        self._items.pop(name.lower(), None)

    def get(
        self,
        name: str,
    ):

        return self._items.get(name.lower())

    def exists(
        self,
        name: str,
    ):

        return name.lower() in self._items

    def names(self):

        return sorted(self._items.keys())

    def values(self):

        return list(self._items.values())

    def __len__(self):

        return len(self._items)
