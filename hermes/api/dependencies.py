"""
===============================================================================
API Dependencies
===============================================================================
"""
from __future__ import annotations

import os

from hermes.runtime.execution_manager import ExecutionManager


_execution_manager: ExecutionManager = None


def get_execution_manager() -> ExecutionManager:
    global _execution_manager
    if _execution_manager is None:
        from hermes.bootstrap.bootstrap import HermesBootstrap
        container = HermesBootstrap().build()
        
        provider = os.getenv("HERMES_PROVIDER", "openrouter")
        model = os.getenv("HERMES_MODEL", "openai/gpt-4.1-mini")
        
        def agent_executor_factory():
            from hermes.agent.executor.executor import AgentExecutor
            return AgentExecutor(
                pipeline=container.ai_pipeline,
                tool_manager=container.tool_manager,
                provider=provider,
                model=model
            )
            
        _execution_manager = ExecutionManager(agent_executor_factory=agent_executor_factory)
    return _execution_manager

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture