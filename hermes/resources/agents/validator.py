"""
===============================================================================
Hermes Agent Validator
===============================================================================
"""

from __future__ import annotations

from .agent import RuntimeAgent
from .exceptions import AgentValidationError


class AgentValidator:
    """
    Validates Runtime Agents.
    """

    def validate(
        self,
        agent: RuntimeAgent,
    ) -> None:

        if not agent.id.strip():

            raise AgentValidationError("Agent id cannot be empty.")

        if not agent.name.strip():

            raise AgentValidationError("Agent name cannot be empty.")

        if agent.temperature < 0:

            raise AgentValidationError("Temperature cannot be negative.")

        if agent.temperature > 2:

            raise AgentValidationError("Temperature cannot exceed 2.0.")

        if agent.max_context <= 0:

            raise AgentValidationError("Maximum context must be positive.")
