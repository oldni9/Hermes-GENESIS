"""
===============================================================================
Hermes Genesis Constants
===============================================================================

Global constants used throughout Hermes.

Only true constants belong here.

===============================================================================
"""

from __future__ import annotations

from .metadata import HERMES


HERMES_NAME = HERMES.name
HERMES_VERSION = HERMES.version
HERMES_CODENAME = HERMES.codename


DEFAULT_ENCODING = "utf-8"

DEFAULT_LOG_LEVEL = "INFO"

DEFAULT_TIMEZONE = "UTC"

MAX_PRIORITY = 100
MIN_PRIORITY = 0
DEFAULT_PRIORITY = 50