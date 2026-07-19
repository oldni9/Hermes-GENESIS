"""
===============================================================================
Tests for Plugin Manager
===============================================================================
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from hermes.plugins import PluginManager, Plugin, CommandDefinition, EventHandler
from hermes.plugins.exceptions import PluginInitializationError
from hermes.ai.tool import Tool


class MockPlugin(Plugin):
    def __init__(self, fail_init: bool = False):
        super().__init__()
        self._fail_init = fail_init
        self._initialized = False
        self._shutdown = False

    @property
    def id(self) -> str:
        return "test"

    @property
    def name(self) -> str:
        return "Mock Plugin"

    @property
    def version(self) -> str:
        return "1.0"

    @property
    def description(self) -> str:
        return "A mock plugin for testing."

    def initialize(self) -> None:
        if self._fail_init:
            raise ValueError("Intentional failure")
        self._initialized = True

    def shutdown(self) -> None:
        self._shutdown = True

    def tools(self) -> list[Tool]:
        return [Tool(name="test_tool")]

    def commands(self) -> list[CommandDefinition]:
        return [CommandDefinition(name="test_command", handler=lambda: None)]

    def events(self) -> list[EventHandler]:
        return [EventHandler(event="test_event", handler=lambda: None)]


def test_manager_register_plugin():
    manager = PluginManager()
    plugin = MockPlugin()
    manager.registry.register(plugin)
    assert manager.registry.exists("test")


def test_manager_initialize_all():
    manager = PluginManager()
    plugin = MockPlugin()
    manager.registry.register(plugin)
    manager.initialize_all()
    assert plugin._initialized is True
    assert manager._initialized is True


def test_manager_initialize_failure_with_rollback():
    manager = PluginManager()
    # Both plugins inherit from MockPlugin to get _initialized and _shutdown
    class PluginA(MockPlugin):
        @property
        def id(self) -> str:
            return "plugin_a"
        @property
        def name(self) -> str:
            return "Plugin A"
        @property
        def version(self) -> str:
            return "1.0"
        @property
        def description(self) -> str:
            return ""
        def initialize(self) -> None:
            self._initialized = True  # succeeds
    class PluginB(MockPlugin):
        @property
        def id(self) -> str:
            return "plugin_b"
        @property
        def name(self) -> str:
            return "Plugin B"
        @property
        def version(self) -> str:
            return "1.0"
        @property
        def description(self) -> str:
            return ""
        def initialize(self) -> None:
            raise ValueError("Intentional failure")
    plugin_a = PluginA()
    plugin_b = PluginB()
    manager.registry.register(plugin_a)
    manager.registry.register(plugin_b)
    with pytest.raises(PluginInitializationError):
        manager.initialize_all()
    # plugin_a should have been shut down after rollback
    assert plugin_a._shutdown is True
    # plugin_b should not have been initialized
    assert plugin_b._initialized is False
    # manager should remain not initialized
    assert manager._initialized is False


def test_manager_shutdown_all():
    manager = PluginManager()
    plugin = MockPlugin()
    manager.registry.register(plugin)
    manager.initialize_all()
    manager.shutdown_all()
    assert plugin._shutdown is True
    assert manager._initialized is False
    # Cache should be invalidated
    assert manager._cached_tools is None


def test_manager_unload_plugin():
    manager = PluginManager()
    plugin = MockPlugin()
    manager.registry.register(plugin)
    manager.initialize_all()
    manager.unload_plugin("test")
    assert not manager.registry.exists("test")
    assert plugin._shutdown is True
    # Cache should be invalidated
    assert manager._cached_tools is None


def _load_plugin_from_path(path: Path) -> Plugin:
    """Load a plugin from a file using importlib.util."""
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Failed to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "PLUGIN_CLASS"):
        raise AttributeError("Module does not define PLUGIN_CLASS")
    plugin_class = getattr(module, "PLUGIN_CLASS")
    if not issubclass(plugin_class, Plugin):
        raise TypeError("PLUGIN_CLASS is not a Plugin subclass")
    return plugin_class()


def test_manager_aggregation_and_cache(tmp_path):
    # Create two temporary plugin modules
    mod_content1 = """
from hermes.plugins import Plugin
from hermes.ai.tool import Tool

class TempTestPlugin(Plugin):
    @property
    def id(self) -> str:
        return "test"
    @property
    def name(self) -> str:
        return "Test Plugin"
    @property
    def version(self) -> str:
        return "1.0"
    @property
    def description(self) -> str:
        return "A test plugin."
    def tools(self) -> list[Tool]:
        return [Tool(name="test_tool")]

PLUGIN_CLASS = TempTestPlugin
"""
    mod_content2 = """
from hermes.plugins import Plugin
from hermes.ai.tool import Tool

class AnotherTempPlugin(Plugin):
    @property
    def id(self) -> str:
        return "another"
    @property
    def name(self) -> str:
        return "Another Plugin"
    @property
    def version(self) -> str:
        return "1.0"
    @property
    def description(self) -> str:
        return "Another plugin."
    def tools(self) -> list[Tool]:
        return [Tool(name="another_tool")]

PLUGIN_CLASS = AnotherTempPlugin
"""
    mod_path1 = tmp_path / "test_plugin.py"
    mod_path2 = tmp_path / "another_plugin.py"
    mod_path1.write_text(mod_content1)
    mod_path2.write_text(mod_content2)

    # Load plugins manually
    plugin1 = _load_plugin_from_path(mod_path1)
    plugin2 = _load_plugin_from_path(mod_path2)

    manager = PluginManager()

    # Register first plugin
    manager.registry.register(plugin1)
    # First call builds cache
    tools = manager.all_tools()
    assert len(tools) == 1
    assert tools[0].name == "test_tool"

    # Second call uses cache
    tools2 = manager.all_tools()
    assert tools2 is tools  # same object

    # Register second plugin
    manager.registry.register(plugin2)
    # Manually invalidate cache to reflect the new plugin
    manager._invalidate_cache()

    # Cache should be invalidated; next call rebuilds
    tools3 = manager.all_tools()
    assert len(tools3) == 2
    # Check both tools are present
    names = [t.name for t in tools3]
    assert "test_tool" in names
    assert "another_tool" in names
    assert tools3 is not tools


def test_cache_invalidation_on_unload(tmp_path):
    mod_content = """
from hermes.plugins import Plugin
from hermes.ai.tool import Tool

class TempTestPlugin(Plugin):
    @property
    def id(self) -> str:
        return "test"
    @property
    def name(self) -> str:
        return "Test Plugin"
    @property
    def version(self) -> str:
        return "1.0"
    @property
    def description(self) -> str:
        return "A test plugin."
    def tools(self) -> list[Tool]:
        return [Tool(name="test_tool")]

PLUGIN_CLASS = TempTestPlugin
"""
    mod_path = tmp_path / "test_plugin.py"
    mod_path.write_text(mod_content)

    plugin = _load_plugin_from_path(mod_path)
    manager = PluginManager()
    manager.registry.register(plugin)

    # Build cache
    tools = manager.all_tools()
    assert len(tools) == 1
    assert tools[0].name == "test_tool"

    # Unload plugin
    manager.unload_plugin("test")
    # Cache should be invalidated
    assert manager._cached_tools is None
    # Next call should return empty list
    tools2 = manager.all_tools()
    assert len(tools2) == 0