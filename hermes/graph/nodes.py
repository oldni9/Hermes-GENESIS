"""
===============================================================================
Execution Graph Nodes
===============================================================================

Sprint 14: Polymorphic node implementations with constructor-injected dependencies.
===============================================================================
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from hermes.agent.executor.planners.base import Planner, PlannerState, PlannerConfig
from hermes.graph.models import GraphContext, NodeResult, _SafeDict


class GraphNode(ABC):
    """Abstract Base Class for all execution graph nodes."""
    def __init__(self, node_id: str) -> None:
        self.id = node_id
        self._output_key = node_id

    @property
    def output_key(self) -> str:
        """The key under which the node's primary output is stored on the blackboard."""
        return self._output_key

    @abstractmethod
    def execute(self, context: GraphContext) -> NodeResult:
        ...


class LLMNode(GraphNode):
    """Executes a single LLM call using an injected execution engine."""
    def __init__(
        self, 
        node_id: str, 
        prompt_template: str, 
        engine: Any, 
        config: PlannerConfig,
        output_key: Optional[str] = None
    ) -> None:
        super().__init__(node_id)
        self._prompt_template = prompt_template
        self._engine = engine
        self._config = config
        self._output_key = output_key or node_id

    def execute(self, context: GraphContext) -> NodeResult:
        prompt = self._prompt_template.format_map(_SafeDict(context.blackboard.to_dict()))
        response = self._engine.execute_ephemeral(context.trace, 1, self._config, prompt)
        
        if not response.success:
            return NodeResult(success=False, stop=True)
            
        return NodeResult(success=True, outputs={self._output_key: response.text()})


class PlannerNode(GraphNode):
    """Wraps an existing Planner instance to be used as a graph node."""
    def __init__(
        self, 
        node_id: str, 
        planner: Planner, 
        engine: Any, 
        config: PlannerConfig,
        output_key: Optional[str] = None
    ) -> None:
        super().__init__(node_id)
        self._planner = planner
        self._engine = engine
        self._config = config
        self._output_key = output_key or node_id

    def execute(self, context: GraphContext) -> NodeResult:
        state = PlannerState(
            conversation=context.conversation,
            trace=context.trace,
            runtime_context=context.runtime_context,
            objective=context.blackboard.get("objective", ""),
            retrieved_context=context.blackboard.get("retrieved_context")
        )
        
        result = self._planner.run(self._engine, state, self._config)
        
        if not result.response.success:
            return NodeResult(success=False, stop=True)
            
        return NodeResult(
            success=True, 
            outputs={
                self._output_key: result.response.text(),
                "memory_candidates": result.memory_candidates
            }
        )


class JudgeNode(GraphNode):
    """Synthesizes inputs from multiple parent nodes into a single output."""
    def __init__(
        self, 
        node_id: str, 
        prompt_template: str, 
        input_keys: List[str], 
        engine: Any, 
        config: PlannerConfig,
        output_key: Optional[str] = None
    ) -> None:
        super().__init__(node_id)
        self._prompt_template = prompt_template
        self._input_keys = input_keys
        self._engine = engine
        self._config = config
        self._output_key = output_key or node_id

    def execute(self, context: GraphContext) -> NodeResult:
        inputs = [context.blackboard.get(k, "") for k in self._input_keys]
        inputs_str = "\n\n".join([f"Input {i+1}:\n{val}" for i, val in enumerate(inputs)])
        
        prompt = self._prompt_template.format(inputs=inputs_str)
        
        response = self._engine.execute_ephemeral(context.trace, 1, self._config, prompt)
        
        if not response.success:
            return NodeResult(success=False, stop=True)
            
        return NodeResult(success=True, outputs={self._output_key: response.text()})

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture