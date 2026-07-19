"""
===============================================================================
Hermes Runtime Adapters
===============================================================================

Runtime Adapter Object System.

This package owns adapter Runtime Objects.

Adapters represent external execution backends such as:

    • Ollama
    • LM Studio
    • OpenRouter
    • Groq
    • OpenAI
    • Local REST APIs
    • Future Plugins

Adapters are Runtime Objects.

No adapter is hardcoded into Hermes.

===============================================================================
"""

from .adapter import RuntimeAdapter
from .registry import AdapterRegistry
from .manager import AdapterManager
from .loader import AdapterLoader
from .validator import AdapterValidator

__all__ = [
    "RuntimeAdapter",
    "AdapterRegistry",
    "AdapterManager",
    "AdapterLoader",
    "AdapterValidator",
]
