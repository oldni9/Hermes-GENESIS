"""
===============================================================================
Hermes Agent Runtime
===============================================================================
"""
from __future__ import annotations

import uuid
from typing import Dict, List, Optional

from hermes.planning.planner import Planner
from hermes.planning.plan_to_execution_graph import PlanToExecutionGraphConverter
from hermes.scheduler.engine import SchedulerEngine
from hermes.reasoning.optimizer import GraphOptimizer
from hermes.ai.tool import Tool

from hermes.agent.agent import Agent
from hermes.agent.memory import AgentMemory
from hermes.agent.response import AgentResponse
from hermes.agent.session import AgentSession
from hermes.agent.exceptions import AgentNotFound, AgentError


class AgentRuntime:
    """
    Orchestrates the agent execution pipeline and manages agent lifecycle.
    """

    def __init__(
        self,
        planner: Planner,
        converter: PlanToExecutionGraphConverter,
        scheduler: SchedulerEngine,
        optimizer: Optional[GraphOptimizer] = None,
    ) -> None:
        self._planner = planner
        self._converter = converter
        self._scheduler = scheduler
        self._optimizer = optimizer
        self._agents: Dict[str, Agent] = {}

    # ------------------------------------------------------------------
    # Agent lifecycle
    # ------------------------------------------------------------------

    def create_agent(
        self,
        system_prompt: str,
        tools: Optional[List[Tool]] = None,
        memory: Optional[AgentMemory] = None,
        agent_id: Optional[str] = None,
    ) -> Agent:
        """
        Create a new agent.
        If agent_id is not provided, a UUID4 is auto-generated.
        """
        if agent_id is None:
            agent_id = str(uuid.uuid4())
        agent = Agent(
            agent_id=agent_id,
            system_prompt=system_prompt,
            tools=tools,
            memory=memory,
        )
        self._agents[agent_id] = agent
        return agent

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Retrieve an agent by ID."""
        return self._agents.get(agent_id)

    def list_agents(self) -> List[Agent]:
        """List all active agents."""
        return list(self._agents.values())

    def destroy_agent(self, agent_id: str) -> None:
        """Remove an agent and its state."""
        if agent_id not in self._agents:
            raise AgentNotFound(f"Agent '{agent_id}' not found")
        del self._agents[agent_id]

    def reset_session(self, agent_id: str) -> None:
        """Reset the session (conversation) of an agent."""
        agent = self.get_agent(agent_id)
        if agent is None:
            raise AgentNotFound(f"Agent '{agent_id}' not found")
        # Replace the session with a fresh one
        agent._session = AgentSession()

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def execute(
        self,
        agent: Agent,
        user_input: str,
        *,
        stream: bool = False,  # reserved for future streaming support
    ) -> AgentResponse:
        """
        Execute a single user input through the entire pipeline:
            Planner → Plan
            Converter → ExecutionGraph
            Optimizer (optional) → OptimizedGraph
            Scheduler → Execution
        Aggregates results and updates session/memory.
        """
        if stream:
            # Streaming not yet implemented; raise a clear error.
            raise NotImplementedError("Streaming is not yet supported in this version.")

        # 1. Plan
        plan = self._planner.plan(user_input)

        # 2. Convert
        graph = self._converter.convert(plan)

        # 3. Optimize (if available)
        if self._optimizer is not None:
            result = self._optimizer.optimize(graph)
            graph = result.graph
            # Metadata is available in result.metadata, but we ignore it for now.

        # 4. Schedule
        processed_graph = self._scheduler.process(graph)

        # 5. Build response
        # Since the scheduler executes in-place, we need to extract results.
        # For simplicity, we'll combine all node outputs into a single text.
        # In a real implementation, you'd aggregate results from the execution.
        # This is a placeholder that works with the current scheduler behavior.
        outputs: List[str] = []
        for node in processed_graph.all_nodes():
            if node.payload:
                outputs.append(str(node.payload))
        text = "\n".join(outputs) if outputs else "No output from execution."

        # Update agent's session conversation
        agent.session.conversation.user(user_input)
        agent.session.conversation.assistant(text)

        # Update agent memory (store the user input and response)
        agent.memory.add(f"User: {user_input}", tags=["user_input"])
        agent.memory.add(f"Assistant: {text}", tags=["assistant_response"])

        return AgentResponse(
            success=True,
            text=text,
            session=agent.session,
            metadata={"nodes": len(processed_graph.all_nodes())},
            plan=plan,
            execution_graph=processed_graph,
        )