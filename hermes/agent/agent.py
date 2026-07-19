"""
===============================================================================
Hermes Agent
===============================================================================
"""
from __future__ import annotations

from typing import List, Optional

from hermes.ai.tool import Tool
from hermes.agent.session import AgentSession
from hermes.agent.memory import AgentMemory


class Agent:
    """
    Lightweight agent container.
    Holds identity, system prompt, tools, session, and memory.
    Does not execute; execution is handled by AgentRuntime.
    """

    def __init__(
        self,
        agent_id: str,
        system_prompt: str,
        tools: Optional[List[Tool]] = None,
        memory: Optional[AgentMemory] = None,
    ) -> None:
        self._id = agent_id
        self._system_prompt = system_prompt
        self._tools = tools if tools is not None else []
        self._memory = memory if memory is not None else AgentMemory()
        self._session = AgentSession()

    @property
    def id(self) -> str:
        return self._id

    @property
    def system_prompt(self) -> str:
        return self._system_prompt

    @property
    def tools(self) -> List[Tool]:
        return self._tools

    @property
    def memory(self) -> AgentMemory:
        return self._memory

    @property
    def session(self) -> AgentSession:
        return self._session