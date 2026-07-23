"""
Parallel Execution Node
Sprint 16 Update:
MergeStrategy implementations now aggregate memory_candidates from branches.
"""
from __future__ import annotations

import copy
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple

from hermes.agent.executor.planners.base import PlannerConfig
from hermes.agent.executor.trace import TraceEventType
from hermes.runtime.parallel import ParallelJob, ParallelResult
from hermes.graph.models import ExecutionGraph, GraphContext, GraphExecutionError, GraphResult, GraphRunner, NodeMetadata, NodeResult, Blackboard, ParallelRunner
from hermes.graph.nodes.subgraph import SubgraphNode


class ParallelExecutionPolicy(str):
    FAIL_FAST = "fail_fast"
    ALL_SUCCESS = "all_success"
    BEST_EFFORT = "best_effort"


class MergeStrategy(ABC):
    """Protocol for merging results from parallel branches."""
    @abstractmethod
    def merge(self, results: List[GraphResult]) -> NodeResult:
        ...


class ListMergeStrategy(MergeStrategy):
    """Collects outputs from successful branches into a single list under 'merged_outputs'."""
    def merge(self, results: List[GraphResult]) -> NodeResult:
        merged_outputs = []
        branch_meta = []
        all_candidates = []

        for res in results:
            if res.success:
                merged_outputs.append(res.outputs)
                branch_meta.append(res.to_node_result().metadata)
                all_candidates.extend(res.memory_candidates)

        return NodeResult(
            success=all(res.success for res in results),
            outputs={"merged_outputs": merged_outputs},
            metadata=NodeMetadata(
                branch_metadata=tuple(branch_meta),
                memory_candidates=tuple(all_candidates)
            )
        )


class TextConcatStrategy(MergeStrategy):
    """Concatenates 'text' outputs from successful branches."""
    def merge(self, results: List[GraphResult]) -> NodeResult:
        texts = []
        branch_meta = []
        all_candidates = []

        for res in results:
            if res.success:
                texts.append(res.outputs.get("text", ""))
                branch_meta.append(res.to_node_result().metadata)
                all_candidates.extend(res.memory_candidates)

        return NodeResult(
            success=all(res.success for res in results),
            outputs={"text": "\n\n".join(texts)},
            metadata=NodeMetadata(
                branch_metadata=tuple(branch_meta),
                memory_candidates=tuple(all_candidates)
            )
        )


class ParallelNode(SubgraphNode):
    """
    A composite node that executes multiple subgraphs in parallel.
    Each branch receives a cloned blackboard to ensure complete isolation.
    """

    def __init__(
        self,
        node_id: str,
        branches: List[ExecutionGraph],
        merge_strategy: MergeStrategy,
        parallel_runner: ParallelRunner,
        graph_runner: GraphRunner,
        policy: str = ParallelExecutionPolicy.ALL_SUCCESS,
        output_key: str = "text"
    ) -> None:
        super().__init__(node_id, graph_runner, output_key)
        if not branches:
            raise ValueError("ParallelNode requires at least one branch.")

        self._branches = branches
        self._merge_strategy = merge_strategy
        self._parallel_runner = parallel_runner
        self._policy = policy

    def execute(self, context: GraphContext) -> NodeResult:
        context.trace.add_event(1, TraceEventType.PARALLEL_STARTED, {
            "node_id": self.id,
            "branches": len(self._branches)
        })

        jobs: List[ParallelJob] = []

        for i, branch_graph in enumerate(self._branches):
            cloned_blackboard = Blackboard(copy.deepcopy(context.blackboard.to_dict()))

            def make_task(graph: ExecutionGraph, bb: Blackboard, idx: int):
                def task() -> GraphResult:
                    context.trace.add_event(1, TraceEventType.PARALLEL_BRANCH_STARTED, {
                        "node_id": self.id, "branch_idx": idx
                    })
                    child_context = GraphContext(
                        conversation=context.conversation,
                        runtime_context=context.runtime_context,
                        trace=context.trace,
                        blackboard=bb
                    )
                    graph_result = self.run_subgraph(graph, child_context)
                    context.trace.add_event(1, TraceEventType.PARALLEL_BRANCH_FINISHED, {
                        "node_id": self.id, "branch_idx": idx, "success": graph_result.success
                    })
                    return graph_result
                return task

            jobs.append(ParallelJob(id=f"{self.id}_branch_{i}", fn=make_task(branch_graph, cloned_blackboard, i)))

        results = self._parallel_runner.execute(jobs)

        successful_results: List[GraphResult] = []
        failed_results: List[ParallelResult] = []

        for r in results:
            if r.success and r.value is not None and r.value.success:
                successful_results.append(r.value)
            else:
                failed_results.append(r)

        if failed_results and self._policy == ParallelExecutionPolicy.FAIL_FAST:
            exc = failed_results[0].exception or Exception("Unknown error")
            raise GraphExecutionError(
                self.id, context.trace, context.blackboard.to_dict(),
                exc
            )

        context.trace.add_event(1, TraceEventType.MERGE_STARTED, {"node_id": self.id})
        try:
            merged_result = self._merge_strategy.merge(successful_results)

            if self._policy == ParallelExecutionPolicy.ALL_SUCCESS and failed_results:
                err_details = [str(r.exception) for r in failed_results if r.exception]
                new_outputs = copy.deepcopy(merged_result.outputs)
                new_outputs["error"] = f"{len(failed_results)} branches failed: {err_details}"
                merged_result = NodeResult(
                    success=False,
                    stop=True,
                    outputs=new_outputs,
                    metadata=merged_result.metadata
                )
            elif not successful_results:
                new_outputs = copy.deepcopy(merged_result.outputs)
                new_outputs["error"] = "All parallel branches failed."
                merged_result = NodeResult(
                    success=False,
                    stop=True,
                    outputs=new_outputs,
                    metadata=merged_result.metadata
                )

        except Exception as e:
            context.trace.add_event(1, TraceEventType.MERGE_FINISHED, {"node_id": self.id, "success": False})
            raise GraphExecutionError(self.id, context.trace, context.blackboard.to_dict(), e)

        context.trace.add_event(1, TraceEventType.MERGE_FINISHED, {"node_id": self.id, "success": merged_result.success})
        context.trace.add_event(1, TraceEventType.PARALLEL_COMPLETED, {
            "node_id": self.id, "success_count": len(successful_results)
        })

        return merged_result

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture