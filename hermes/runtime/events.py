"""
===============================================================================
Hermes Runtime Events
===============================================================================
"""

from __future__ import annotations

from collections import defaultdict


class RuntimeEvents:

    def __init__(self):

        self._listeners = defaultdict(list)

    def on(
        self,
        event: str,
        callback,
    ):

        self._listeners[event].append(callback)

    def emit(
        self,
        event: str,
        *args,
        **kwargs,
    ):

        for callback in self._listeners[event]:

            callback(*args, **kwargs)
