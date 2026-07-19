"""
===============================================================================
Hermes Plugin Manager
===============================================================================
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from hermes.ai.tool import Tool
from hermes.memory.backend import MemoryBackend
from hermes.providers.provider import Provider

from .plugin import Plugin, CommandDefinition, EventHandler
from .registry import PluginRegistry
from .loader import PluginLoader
from .exceptions import PluginError, PluginInitializationError


class PluginManager:
    """
    Manages plugin lifecycle, registration, and capability aggregation.
    """

    def __init__(self) -> None:
        self._registry = PluginRegistry()
        self._loader = PluginLoader()
        self._initialized = False
        self._cached_tools: Optional[List[Tool]] = None
        self._cached_memory_backends: Optional[List[MemoryBackend]] = None
        self._cached_providers: Optional[List[Provider]] = None
        self._cached_commands: Optional[List[CommandDefinition]] = None
        self._cached_events: Optional[List[EventHandler]] = None

    @property
    def registry(self) -> PluginRegistry:
        """Return the plugin registry."""
        return self._registry

    @property
    def loader(self) -> PluginLoader:
        """Return the plugin loader."""
        return self._loader

    def _invalidate_cache(self) -> None:
        """Invalidate all aggregated capability caches."""
        self._cached_tools = None
        self._cached_memory_backends = None
        self._cached_providers = None
        self._cached_commands = None
        self._cached_events = None

    def load_plugin(self, module_path: str) -> Plugin:
        """
        Load a plugin from a module path, register it, and initialize it.
        Returns the loaded plugin.
        Raises PluginError on failure.
        """
        if self._initialized:
            raise PluginError("Cannot load plugins after initialization.")

        plugin = self._loader.load(module_path)
        self._registry.register(plugin)
        self._invalidate_cache()
        return plugin

    def unload_plugin(self, plugin_id: str) -> None:
        """
        Unload a plugin by ID.
        This will call shutdown on the plugin and remove it from the registry.
        """
        plugin = self._registry.get(plugin_id)
        if plugin is None:
            return
        try:
            plugin.shutdown()
        except Exception:
            # Log and continue
            pass
        self._registry.remove(plugin_id)
        self._invalidate_cache()

    def initialize_all(self) -> None:
        """
        Initialize all registered plugins.
        Raises PluginInitializationError if any plugin fails to initialize.
        """
        initialized: List[Plugin] = []
        try:
            for plugin in self._registry.list():
                plugin.initialize()
                initialized.append(plugin)
        except Exception as e:
            # Roll back: shutdown all previously initialized plugins
            for p in reversed(initialized):
                try:
                    p.shutdown()
                except Exception:
                    pass
            raise PluginInitializationError(f"Plugin '{plugin.id}' failed to initialize: {e}") from e
        self._initialized = True

    def shutdown_all(self) -> None:
        """
        Shut down all registered plugins and reset initialization state.
        """
        for plugin in self._registry.list():
            try:
                plugin.shutdown()
            except Exception:
                # Log and continue; we want to shut down as much as possible.
                pass
        self._initialized = False
        self._invalidate_cache()

    # ------------------------------------------------------------------
    # Aggregated capabilities (with caching)
    # ------------------------------------------------------------------

    def all_tools(self) -> List[Tool]:
        """Aggregate all tools from all plugins."""
        if self._cached_tools is None:
            tools: List[Tool] = []
            for plugin in self._registry.list():
                tools.extend(plugin.tools())
            self._cached_tools = tools
        return self._cached_tools

    def all_memory_backends(self) -> List[MemoryBackend]:
        """Aggregate all memory backends from all plugins."""
        if self._cached_memory_backends is None:
            backends: List[MemoryBackend] = []
            for plugin in self._registry.list():
                backends.extend(plugin.memory_backends())
            self._cached_memory_backends = backends
        return self._cached_memory_backends

    def all_providers(self) -> List[Provider]:
        """Aggregate all providers from all plugins."""
        if self._cached_providers is None:
            providers: List[Provider] = []
            for plugin in self._registry.list():
                providers.extend(plugin.providers())
            self._cached_providers = providers
        return self._cached_providers

    def all_commands(self) -> List[CommandDefinition]:
        """Aggregate all commands from all plugins."""
        if self._cached_commands is None:
            commands: List[CommandDefinition] = []
            for plugin in self._registry.list():
                commands.extend(plugin.commands())
            self._cached_commands = commands
        return self._cached_commands

    def all_events(self) -> List[EventHandler]:
        """Aggregate all event handlers from all plugins."""
        if self._cached_events is None:
            events: List[EventHandler] = []
            for plugin in self._registry.list():
                events.extend(plugin.events())
            self._cached_events = events
        return self._cached_events