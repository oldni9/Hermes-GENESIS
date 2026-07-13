"""
===============================================================================
Hermes Model Types
===============================================================================
"""

from enum import Enum


class ModelType(str, Enum):

    LLAMA32 = "llama3.2:3b"

    GLM47_FLASH = "GLM-4.7-Flash"

    GLM46V_FLASH = "GLM-4.6V-Flash"

    GLM52 = "GLM-5.2"

    DEEPSEEK_V3 = "DeepSeek-V3"

    QWEN3 = "Qwen3"

    GPT41 = "gpt-4.1"

    CLAUDE4 = "claude-4"

    GEMINI25 = "gemini-2.5"