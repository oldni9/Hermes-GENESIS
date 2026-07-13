"""
===============================================================================
Hermes Profile Exceptions
===============================================================================
"""

from __future__ import annotations


class ProfileError(Exception):
    """
    Base Profile Exception.
    """


class ProfileAlreadyExists(ProfileError):
    """
    Profile already exists.
    """


class ProfileNotFound(ProfileError):
    """
    Profile not found.
    """


class ProfileValidationError(ProfileError):
    """
    Invalid Runtime Profile.
    """