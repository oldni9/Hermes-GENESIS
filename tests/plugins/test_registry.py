"""
===============================================================================
Tests for Plugin Registry
===============================================================================
"""
from __future__ import annotations

import pytest

from hermes.plugins import Plugin, PluginRegistry
from hermes.plugins.exceptions import PluginRegistrationError


class DummyPlugin(Plugin):
    @property
    def id(self) -> str:
        return "dummy"

    @property
    def name(self) -> str:
        return "Dummy"

    @property
    def version(self) -> str:
        return "1.0"

    @property
    def description(self) -> str:
        return ""


class InvalidPlugin(Plugin):
    @property
    def id(self) -> str:
        return ""

    @property
    def name(self) -> str:
        return ""

    @property
    def version(self) -> str:
        return ""

    @property
    def description(self) -> str:
        return ""


def test_registry_register():
    registry = PluginRegistry()
    plugin = DummyPlugin()
    registry.register(plugin)
    assert registry.exists("dummy")
    assert registry.get("dummy") is plugin


def test_registry_duplicate():
    registry = PluginRegistry()
    plugin = DummyPlugin()
    registry.register(plugin)
    with pytest.raises(PluginRegistrationError, match="already registered"):
        registry.register(DummyPlugin())


def test_registry_invalid_plugin():
    registry = PluginRegistry()
    plugin = InvalidPlugin()
    with pytest.raises(PluginRegistrationError, match="non-empty string"):
        registry.register(plugin)


def test_registry_remove():
    registry = PluginRegistry()
    plugin = DummyPlugin()
    registry.register(plugin)
    registry.remove("dummy")
    assert not registry.exists("dummy")
    assert registry.get("dummy") is None


def test_registry_list():
    registry = PluginRegistry()
    p1 = DummyPlugin()
    class OtherPlugin(Plugin):
        @property
        def id(self) -> str:
            return "other"
        @property
        def name(self) -> str:
            return "Other"
        @property
        def version(self) -> str:
            return "1.0"
        @property
        def description(self) -> str:
            return ""
    p2 = OtherPlugin()
    registry.register(p1)
    registry.register(p2)
    plugins = registry.list()
    assert len(plugins) == 2
    assert plugins[0] is p1
    assert plugins[1] is p2


def test_registry_len_iter():
    registry = PluginRegistry()
    p1 = DummyPlugin()
    class OtherPlugin(Plugin):
        @property
        def id(self) -> str:
            return "other"
        @property
        def name(self) -> str:
            return "Other"
        @property
        def version(self) -> str:
            return "1.0"
        @property
        def description(self) -> str:
            return ""
    p2 = OtherPlugin()
    registry.register(p1)
    registry.register(p2)
    assert len(registry) == 2
    plugins = list(registry)
    assert len(plugins) == 2
    assert p1 in plugins
    assert p2 in plugins