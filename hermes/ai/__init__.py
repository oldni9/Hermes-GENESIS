"""
===============================================================================
Hermes AI Providers

Built-in AI providers shipped with Hermes.

Author:
    Aryan + ChatGPT
===============================================================================
"""

from hermes.ai.cache import AICache
from hermes.ai.context import AIContext
from hermes.ai.conversation import AIConversation, ConversationMessage, ConversationState
from hermes.ai.conversation_prompt_builder import ConversationPromptBuilder
from hermes.ai.manager import AIManager
from hermes.ai.metadata import AIMetadata
from hermes.ai.pipeline import AIPipeline
from hermes.ai.prompt import Prompt, PromptMessage, PromptRole
from hermes.ai.provider import BaseAIProvider
from hermes.ai.registry import AIRegistry
from hermes.ai.request import AIRequest
from hermes.ai.request_builder import RequestBuilder
from hermes.ai.response import AIResponse
from hermes.ai.router import AIRouter
from hermes.ai.session import AISession
from hermes.ai.session_manager import MemorySessionManager, SessionManager
from hermes.ai.tool import Tool, ToolCall, ToolManager, ToolRegistry, ToolResult
from hermes.ai.chat import Chat
from hermes.ai.client import HermesClient
from hermes.ai.middleware import BaseMiddleware, MiddlewareChain, MiddlewareContext, MiddlewareError, MiddlewareShortCircuit

__all__ = [
    "AICache",
    "AIContext",
    "AIConversation",
    "ConversationMessage",
    "ConversationState",
    "ConversationPromptBuilder",
    "AIManager",
    "AIMetadata",
    "AIPipeline",
    "Prompt",
    "PromptMessage",
    "PromptRole",
    "BaseAIProvider",
    "AIRegistry",
    "AIRequest",
    "AIResponse",
    "AIRouter",
    "RequestBuilder",
    "AISession",
    "MemorySessionManager",
    "SessionManager",
    "Tool",
    "ToolCall",
    "ToolManager",
    "ToolRegistry",
    "ToolResult",
    "Chat",
    "HermesClient",
    "BaseMiddleware",
    "MiddlewareChain",
    "MiddlewareContext",
    "MiddlewareError",
    "MiddlewareShortCircuit",
]