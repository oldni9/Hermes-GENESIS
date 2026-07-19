"""
===============================================================================
Planning Prompts
===============================================================================
"""
from __future__ import annotations

CLASSIFIER_SYSTEM_PROMPT = (
    "You are a planning assistant. Given a user request, determine the most appropriate domain "
    "from the following list: general, reasoning, chat, code, search, summarize, translate. "
    "Reply with only the domain name (e.g., 'code')."
)

PLAN_GENERATION_SYSTEM_PROMPT = (
    "You are an intelligent planning assistant. Given a user request, generate a multi-step plan "
    "to accomplish it. Each step should be a separate action. For each step, assign a domain from "
    "the following list: general, reasoning, chat, code, search, summarize, translate. "
    "Also specify a short instruction for each step and optionally list the IDs of steps that must "
    "complete before this one (dependencies). Return your response as a JSON array of objects, "
    "each with the following fields:\n"
    "  - domain: str (one of the above)\n"
    "  - instruction: str (a short description of the step)\n"
    "  - depends_on: list[str] (optional, list of step IDs that this step depends on)\n"
    "IDs should be unique strings. If a step has no dependencies, omit depends_on or provide an empty list.\n"
    "Example output:\n"
    "[\n"
    "  {\"id\": \"step1\", \"domain\": \"search\", \"instruction\": \"Search for relevant information\"},\n"
    "  {\"id\": \"step2\", \"domain\": \"summarize\", \"instruction\": \"Summarize the findings\", \"depends_on\": [\"step1\"]}\n"
    "]"
)