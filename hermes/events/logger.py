"""
===============================================================================
Hermes Event Logger
===============================================================================
"""

from __future__ import annotations

import logging

from hermes.events.event import Event


class EventLogger:

    def __init__(self):

        self.logger = logging.getLogger("Hermes.Events")

    def log(
        self,
        event: Event,
    ):

        self.logger.info(
            "[%s] %s (%s)",
            event.source,
            event.name,
            event.id,
        )
