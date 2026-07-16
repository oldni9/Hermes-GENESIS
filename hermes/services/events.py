"""
===============================================================================
Hermes Service Events

Service event names used throughout Hermes.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations


class ServiceEvents:
    """
    Canonical Hermes service event names.
    """

    REGISTERED = "service.registered"

    UNREGISTERED = "service.unregistered"

    STARTING = "service.starting"

    STARTED = "service.started"

    STOPPING = "service.stopping"

    STOPPED = "service.stopped"

    EXECUTING = "service.executing"

    EXECUTED = "service.executed"

    FAILED = "service.failed"

    CREATED = "service.created"

    DESTROYED = "service.destroyed"