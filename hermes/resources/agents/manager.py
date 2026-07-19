"""
===============================================================================
Hermes Agent Manager
===============================================================================

High-level interface for Runtime Agents.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from .agent import RuntimeAgent
from .exceptions import AgentNotFound
from .registry import AgentRegistry
from .validator import AgentValidator


class AgentManager:
    """
    High-level Runtime Agent manager.
    """

    def __init__(self) -> None:

        self._registry = AgentRegistry()

        self._validator = AgentValidator()

    # ------------------------------------------------------------------

    def register(
        self,
        agent: RuntimeAgent,
    ) -> None:

        self._validator.validate(agent)

        self._registry.register(agent)

    # ------------------------------------------------------------------

    def unregister(
        self,
        agent_id: str,
    ) -> None:

        self._registry.unregister(agent_id)

    # ------------------------------------------------------------------

    def get(
        self,
        agent_id: str,
    ) -> RuntimeAgent:

        agent = self._registry.get(agent_id)

        if agent is None:

            raise AgentNotFound(f"Agent '{agent_id}' does not exist.")

        return agent

    # ------------------------------------------------------------------

    def all(
        self,
    ) -> list[RuntimeAgent]:

        return self._registry.all()

    # ------------------------------------------------------------------

    def enabled(
        self,
    ) -> list[RuntimeAgent]:

        return self._registry.enabled()

    # ------------------------------------------------------------------

    def clear(
        self,
    ) -> None:

        self._registry.clear()
