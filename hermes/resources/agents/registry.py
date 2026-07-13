"""
===============================================================================
Hermes Agent Registry
===============================================================================
"""

from __future__ import annotations

from .agent import RuntimeAgent
from .exceptions import AgentAlreadyExists


class AgentRegistry:

    def __init__(self) -> None:

        self._agents: dict[str, RuntimeAgent] = {}

    # ------------------------------------------------------------------

    def register(
        self,
        agent: RuntimeAgent,
    ) -> None:

        if agent.id in self._agents:

            raise AgentAlreadyExists(
                f"Agent '{agent.id}' already exists."
            )

        self._agents[agent.id] = agent

    # ------------------------------------------------------------------

    def unregister(
        self,
        agent_id: str,
    ) -> None:

        self._agents.pop(agent_id, None)

    # ------------------------------------------------------------------

    def get(
        self,
        agent_id: str,
    ) -> RuntimeAgent | None:

        return self._agents.get(agent_id)

    # ------------------------------------------------------------------

    def all(
        self,
    ) -> list[RuntimeAgent]:

        return list(self._agents.values())

    # ------------------------------------------------------------------

    def enabled(
        self,
    ) -> list[RuntimeAgent]:

        return [
            agent
            for agent in self._agents.values()
            if agent.enabled
        ]

    # ------------------------------------------------------------------

    def clear(
        self,
    ) -> None:

        self._agents.clear()