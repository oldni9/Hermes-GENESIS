"""
===============================================================================
Hermes Plugin Loader
===============================================================================
"""
from __future__ import annotations

import importlib
from typing import Type

from .plugin import Plugin
from .exceptions import PluginLoadError

PLUGIN_ENTRY_POINT = "PLUGIN_CLASS"


class PluginLoader:
    """
    Loads plugins from Python module paths using importlib.
    """

    def _instantiate(self, module_path: str, module) -> Plugin:
        """Internal method to instantiate a plugin from a loaded module."""
        if not hasattr(module, PLUGIN_ENTRY_POINT):
            raise PluginLoadError(
                f"Module '{module_path}' does not define '{PLUGIN_ENTRY_POINT}'."
            )
        plugin_class: Type[Plugin] = getattr(module, PLUGIN_ENTRY_POINT)
        if not (isinstance(plugin_class, type) and issubclass(plugin_class, Plugin)):
            raise PluginLoadError(
                f"'{PLUGIN_ENTRY_POINT}' in '{module_path}' is not a Plugin subclass."
            )
        try:
            plugin = plugin_class()
        except Exception as e:
            raise PluginLoadError(
                f"Failed to instantiate plugin from '{module_path}': {e}"
            ) from e
        return plugin

    def load(self, module_path: str) -> Plugin:
        """
        Load a plugin from a module path.
        The module must define a global variable PLUGIN_CLASS that points to a Plugin subclass.
        Raises PluginLoadError on failure.
        """
        try:
            module = importlib.import_module(module_path)
        except ImportError as e:
            raise PluginLoadError(
                f"Failed to import module '{module_path}': {e}"
            ) from e
        return self._instantiate(module_path, module)

    def reload(self, module_path: str) -> Plugin:
        """
        Reload a plugin by re-importing its module.
        Returns the new plugin instance.
        """
        try:
            module = importlib.import_module(module_path)
        except ImportError as e:
            raise PluginLoadError(
                f"Failed to reload module '{module_path}': {e}"
            ) from e
        module = importlib.reload(module)
        return self._instantiate(module_path, module)