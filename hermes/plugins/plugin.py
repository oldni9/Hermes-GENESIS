"""
===============================================================================
Hermes Plugin Base Class
===============================================================================
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List, Callable

from hermes.ai.tool import Tool
from hermes.memory.backend import MemoryBackend
from hermes.providers.provider import Provider


@dataclass(slots=True, frozen=True)
class CommandDefinition:
    """
    A command definition provided by a plugin.
    """
    name: str
    handler: Callable[..., Any]
    description: str = ""


@dataclass(slots=True, frozen=True)
class EventHandler:
    """
    An event handler provided by a plugin.
    """
    event: str
    handler: Callable[..., Any]
    priority: int = 50


class Plugin(ABC):
    """
    Base class for all Hermes plugins.
    Subclasses should override the lifecycle and capability methods as needed.
    After registration, plugins are considered immutable.
    """

    def __init__(self) -> None:
        self._frozen = False

    def _freeze(self) -> None:
        """Mark the plugin as frozen (immutable after registration)."""
        self._frozen = True

    def __setattr__(self, name: str, value: Any) -> None:
        """
        Override to prevent attribute mutations after freeze.
        Internal attributes (starting with '_') are allowed for runtime state,
        except '_frozen' which becomes immutable after freeze.
        """
        if hasattr(self, "_frozen") and self._frozen:
            if name == "_frozen":
                raise AttributeError("Cannot change frozen status after freeze.")
            if not name.startswith("_"):
                raise AttributeError(f"Cannot set attribute '{name}' on frozen plugin.")
        super().__setattr__(name, value)

    @property
    @abstractmethod
    def id(self) -> str:
        """Unique plugin identifier."""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable plugin name."""
        ...

    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version string."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Plugin description."""
        ...

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def initialize(self) -> None:
        """
        Called when the plugin is loaded and registered.
        Plugins can perform setup here.
        """
        pass

    def shutdown(self) -> None:
        """
        Called when the plugin is unloaded or Hermes shuts down.
        Plugins should release resources here.
        """
        pass

    # ------------------------------------------------------------------
    # Capabilities
    # ------------------------------------------------------------------

    def tools(self) -> List[Tool]:
        """
        Return a list of tools provided by this plugin.
        Default: empty list.
        """
        return []

    def memory_backends(self) -> List[MemoryBackend]:
        """
        Return a list of memory backends provided by this plugin.
        Default: empty list.
        """
        return []

    def providers(self) -> List[Provider]:
        """
        Return a list of providers provided by this plugin.
        Default: empty list.
        """
        return []

    def commands(self) -> List[CommandDefinition]:
        """
        Return a list of command definitions provided by this plugin.
        Default: empty list.
        """
        return []

    def events(self) -> List[EventHandler]:
        """
        Return a list of event handlers provided by this plugin.
        Default: empty list.
        """
        return []