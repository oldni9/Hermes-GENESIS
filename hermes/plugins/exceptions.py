"""
===============================================================================
Hermes Plugin Exceptions
===============================================================================
"""
from __future__ import annotations


class PluginError(Exception):
    """Base exception for plugin-related errors."""


class PluginRegistrationError(PluginError):
    """Raised when plugin registration fails (e.g., duplicate ID)."""


class PluginLoadError(PluginError):
    """Raised when a plugin fails to load (e.g., module not found, import error)."""


class PluginInitializationError(PluginError):
    """Raised when a plugin fails to initialize (e.g., initialize() raises an exception)."""