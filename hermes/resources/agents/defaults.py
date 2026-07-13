"""
===============================================================================
Hermes Default Runtime Agents
===============================================================================

Author:
    Aryan + ChatGPT
===============================================================================
"""

from __future__ import annotations

from .agent import RuntimeAgent


def default_agents() -> list[RuntimeAgent]:

    return [

        RuntimeAgent(
            id="general",
            name="General Assistant",
            description="Default assistant for everyday requests.",
            candidate_models=[
                "default",
            ],
        ),

        RuntimeAgent(
            id="coder",
            name="Code Assistant",
            description="Programming specialist.",
            candidate_models=[
                "default",
            ],
        ),

        RuntimeAgent(
            id="planner",
            name="Planning Agent",
            description="Long-term planning and reasoning.",
            candidate_models=[
                "default",
            ],
        ),
    ]