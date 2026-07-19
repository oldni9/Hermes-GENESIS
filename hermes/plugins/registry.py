"""
===============================================================================
Hermes Plugin Registry
===============================================================================
"""
from __future__ import annotations

from typing import Dict, Iterator, List, Optional

from .plugin import Plugin
from .exceptions import PluginRegistrationError


class PluginRegistry:
    """
    Registry for plugins.
    Stores plugins by ID and preserves registration order.
    After registration, plugins are frozen.
    """

    def __init__(self) -> None:
        self._plugins: Dict[str, Plugin] = {}
        self._order: List[str] = []

    def register(self, plugin: Plugin) -> None:
        """
        Register a plugin.
        Raises PluginRegistrationError if a plugin with the same ID already exists.
        After registration, the plugin is frozen.
        """
        if plugin.id in self._plugins:
            raise PluginRegistrationError(
                f"Plugin '{plugin.id}' is already registered."
            )
        # Validate plugin metadata
        if not isinstance(plugin.id, str) or not plugin.id:
            raise PluginRegistrationError("Plugin id must be a non-empty string.")
        if not isinstance(plugin.name, str) or not plugin.name:
            raise PluginRegistrationError("Plugin name must be a non-empty string.")
        if not isinstance(plugin.version, str) or not plugin.version:
            raise PluginRegistrationError("Plugin version must be a non-empty string.")
        if not isinstance(plugin.description, str):
            raise PluginRegistrationError("Plugin description must be a string.")

        # Freeze the plugin
        plugin._freeze()

        self._plugins[plugin.id] = plugin
        self._order.append(plugin.id)

    def remove(self, plugin_id: str) -> None:
        """
        Remove a plugin from the registry.
        Does NOT call shutdown on the plugin; that is the manager's responsibility.
        """
        if plugin_id in self._plugins:
            self._plugins.pop(plugin_id, None)
            if plugin_id in self._order:
                self._order.remove(plugin_id)

    def get(self, plugin_id: str) -> Optional[Plugin]:
        """Retrieve a plugin by ID."""
        return self._plugins.get(plugin_id)

    def list(self) -> List[Plugin]:
        """Return all registered plugins in registration order."""
        return [self._plugins[pid] for pid in self._order]

    def exists(self, plugin_id: str) -> bool:
        """Check if a plugin with the given ID is registered."""
        return plugin_id in self._plugins

    def __len__(self) -> int:
        return len(self._plugins)

    def __iter__(self) -> Iterator[Plugin]:
        return iter(self.list())

    def __contains__(self, plugin_id: str) -> bool:
        return self.exists(plugin_id)