"""
===============================================================================
Capability Exceptions
===============================================================================
"""


class CapabilityError(Exception):
    """Base capability exception."""


class CapabilityNotFound(CapabilityError):
    """Capability does not exist."""


class CapabilityDisabled(CapabilityError):
    """Capability is disabled."""
