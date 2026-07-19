"""
===============================================================================
Tests for Plugin Base Class
===============================================================================
"""
from __future__ import annotations

import pytest

from hermes.plugins import Plugin, CommandDefinition, EventHandler


class DummyPlugin(Plugin):
    @property
    def id(self) -> str:
        return "dummy"

    @property
    def name(self) -> str:
        return "Dummy Plugin"

    @property
    def version(self) -> str:
        return "1.0"

    @property
    def description(self) -> str:
        return "A dummy plugin for testing."


def test_plugin_base_abstract():
    with pytest.raises(TypeError):
        Plugin()  # type: ignore


def test_plugin_lifecycle():
    plugin = DummyPlugin()
    assert plugin.id == "dummy"
    assert plugin.name == "Dummy Plugin"
    assert plugin.version == "1.0"
    assert plugin.description == "A dummy plugin for testing."

    plugin.initialize()
    plugin.shutdown()


def test_plugin_capabilities_default():
    plugin = DummyPlugin()
    assert plugin.tools() == []
    assert plugin.memory_backends() == []
    assert plugin.providers() == []
    assert plugin.commands() == []
    assert plugin.events() == []


def test_plugin_immutability():
    plugin = DummyPlugin()
    plugin._freeze()
    # Should prevent setting public attributes
    with pytest.raises(AttributeError, match="Cannot set attribute"):
        plugin.some_field = 123
    # Should allow setting internal attributes (starting with '_')
    plugin._internal_counter = 42
    assert plugin._internal_counter == 42
    # Should NOT allow setting _frozen after freeze
    with pytest.raises(AttributeError, match="Cannot change frozen status"):
        plugin._frozen = False