"""
===============================================================================
Hermes Event Priority
===============================================================================
"""

from enum import IntEnum


class EventPriority(IntEnum):

    LOW = 10

    NORMAL = 50

    HIGH = 100

    CRITICAL = 255
