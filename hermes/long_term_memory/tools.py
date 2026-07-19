"""
===============================================================================
Memory Tools
===============================================================================

Dependencies:
    - hermes.ai.tool
    - hermes.long_term_memory.manager

Consumes:
    - ToolManager
    - MemoryManager

Produces:
    - MemoryTools

Public API:
    - MemoryTools

TODO:
    - Return structured data (dicts) instead of strings for tool outputs.
    - Add tool for automatic memory extraction from conversation.
    - Add tool for semantic/hybrid search.
===============================================================================
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from hermes.ai.tool import ParameterType, ToolManager, ToolParameter
from hermes.long_term_memory.manager import MemoryManager


class MemoryTools:
    """
    Provides memory operations as standard Hermes Tools.
    """

    def __init__(self, manager: MemoryManager) -> None:
        self._manager = manager

    def remember(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Save a piece of information to long-term memory."""
        record = self._manager.add(content, metadata)
        return f"Memory saved with ID: {record.id}"

    def forget(self, record_id: str) -> str:
        """Delete a specific memory by its ID."""
        success = self._manager.delete(record_id)
        return "Memory forgotten." if success else "Memory ID not found."

    def search_memories(self, query: str) -> List[Dict[str, Any]]:
        """Search long-term memory for a substring match."""
        records = self._manager.search(query)
        return [
            {"id": r.id, "content": r.content, "metadata": r.metadata}
            for r in records
        ]

    def list_memories(self) -> List[Dict[str, Any]]:
        """List all stored memories."""
        records = self._manager.list()
        return [
            {"id": r.id, "content": r.content, "metadata": r.metadata}
            for r in records
        ]

    def clear_memory(self) -> str:
        """Clear all stored memories permanently."""
        self._manager.clear()
        return "All memories cleared."

    def register(self, tool_manager: ToolManager) -> None:
        """Register all memory tools with the given ToolManager."""
        
        # Tool: remember
        tool_manager.register_function(
            name="remember",
            func=self.remember,
            description="Save a piece of information to long-term memory for later retrieval.",
            parameters=[
                ToolParameter(
                    name="content",
                    type=ParameterType.STRING,
                    description="The information to remember.",
                    required=True,
                ),
                ToolParameter(
                    name="metadata",
                    type=ParameterType.OBJECT,
                    description="Optional metadata dictionary to attach to the memory.",
                    required=False,
                ),
            ],
        )

        # Tool: forget
        tool_manager.register_function(
            name="forget",
            func=self.forget,
            description="Delete a specific memory by its ID.",
            parameters=[
                ToolParameter(
                    name="record_id",
                    type=ParameterType.STRING,
                    description="The ID of the memory to delete.",
                    required=True,
                ),
            ],
        )

        # Tool: search_memories
        tool_manager.register_function(
            name="search_memories",
            func=self.search_memories,
            description="Search long-term memory for information matching the query.",
            parameters=[
                ToolParameter(
                    name="query",
                    type=ParameterType.STRING,
                    description="The search string to look for in memories.",
                    required=True,
                ),
            ],
        )

        # Tool: list_memories
        tool_manager.register_function(
            name="list_memories",
            func=self.list_memories,
            description="List all stored memories.",
            parameters=[],
        )

        # Tool: clear_memory
        tool_manager.register_function(
            name="clear_memory",
            func=self.clear_memory,
            description="Clear all stored memories permanently.",
            parameters=[],
        )