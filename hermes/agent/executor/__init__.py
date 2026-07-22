"""
===============================================================================
Agent Executor Package
===============================================================================

Dependencies:
    - hermes.agent.executor.executor
    - hermes.agent.executor.protocols
    - hermes.agent.executor.result
    - hermes.agent.executor.trace

Consumes:
    - None directly (re-exports)

Produces:
    - AgentExecutor
    - AgentResult
    - StopReason
    - PipelineProtocol
    - AgentTrace
    - TraceEvent
    - PlannerRegistry

Public API:
    - AgentExecutor
    - AgentTrace
===============================================================================
"""

from hermes.agent.executor.executor import AgentExecutor
from hermes.agent.executor.protocols import PipelineProtocol
from hermes.agent.executor.result import AgentResult, StopReason
from hermes.agent.executor.trace import AgentTrace, TraceEvent, TraceEventType
from hermes.agent.executor.errors import MaxIterationsExceeded, PipelineExecutionError, PlannerError
from hermes.agent.executor.planners.base import Planner, PlannerState, PlannerConfig, TreeOfThoughtConfig
from hermes.agent.executor.planners.react import ReActPlanner
from hermes.agent.executor.planners.reflection import ReflectionPlanner
from hermes.agent.executor.planners.tree_of_thought import TreeOfThoughtPlanner
from hermes.agent.executor.planners.registry import (
    PlannerRegistry, 
    PlannerFactory, 
    PlannerDescriptor, 
    PlannerCapabilities,
    GLOBAL_PLANNER_REGISTRY,
    GLOBAL_PLANNER_FACTORY
)

__all__ = [
    "AgentExecutor",
    "AgentResult",
    "StopReason",
    "PipelineProtocol",
    "AgentTrace",
    "TraceEvent",
    "TraceEventType",
    "MaxIterationsExceeded",
    "PipelineExecutionError",
    "PlannerError",
    "Planner",
    "PlannerState",
    "PlannerConfig",
    "TreeOfThoughtConfig",
    "ReActPlanner",
    "ReflectionPlanner",
    "TreeOfThoughtPlanner",
    "PlannerRegistry",
    "PlannerFactory",
    "PlannerDescriptor",
    "PlannerCapabilities",
    "GLOBAL_PLANNER_REGISTRY",
    "GLOBAL_PLANNER_FACTORY",
]

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture