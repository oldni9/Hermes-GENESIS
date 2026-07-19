"""
===============================================================================
Tests for Plugin Loader
===============================================================================
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

from hermes.plugins import PluginLoader
from hermes.plugins.exceptions import PluginLoadError


def test_loader_load_invalid_module():
    loader = PluginLoader()
    with pytest.raises(PluginLoadError, match="Failed to import module"):
        loader.load("nonexistent_module")


def test_loader_load_module_without_plugin(tmp_path):
    # Create a temporary module with no PLUGIN_CLASS
    mod_path = tmp_path / "empty_plugin.py"
    mod_path.write_text("# No plugin class")
    sys.path.insert(0, str(tmp_path))
    try:
        loader = PluginLoader()
        with pytest.raises(PluginLoadError, match="does not define 'PLUGIN_CLASS'"):
            loader.load("empty_plugin")
    finally:
        sys.path.pop(0)


def test_loader_load_plugin(tmp_path):
    # Create a temporary module with a proper plugin
    mod_content = """
from hermes.plugins import Plugin

class TestPlugin(Plugin):
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

PLUGIN_CLASS = TestPlugin
"""
    mod_path = tmp_path / "test_plugin.py"
    mod_path.write_text(mod_content)
    sys.path.insert(0, str(tmp_path))
    try:
        loader = PluginLoader()
        plugin = loader.load("test_plugin")
        assert plugin.id == "test"
        assert plugin.name == "Test Plugin"
        assert plugin.version == "1.0"
        assert plugin.description == "A test plugin."
    finally:
        sys.path.pop(0)


def test_loader_reload(tmp_path):
    # Create a temporary module with a proper plugin, reload it
    mod_content = """
from hermes.plugins import Plugin

class TestPlugin(Plugin):
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

PLUGIN_CLASS = TestPlugin
"""
    mod_path = tmp_path / "test_plugin_reload.py"
    mod_path.write_text(mod_content)
    sys.path.insert(0, str(tmp_path))
    try:
        loader = PluginLoader()
        plugin = loader.load("test_plugin_reload")
        assert plugin.id == "test"
        # Reload should return a new instance
        plugin2 = loader.reload("test_plugin_reload")
        assert plugin2.id == "test"
        assert plugin2 is not plugin
    finally:
        sys.path.pop(0)