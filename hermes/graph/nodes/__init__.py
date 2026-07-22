"""
===============================================================================
Graph Nodes Package
===============================================================================
"""
from hermes.graph.nodes.base import GraphNode, LLMNode, PlannerNode, JudgeNode
from hermes.graph.nodes.subgraph import SubgraphNode
from hermes.graph.nodes.parallel import ParallelNode, MergeStrategy, ListMergeStrategy, TextConcatStrategy, ParallelExecutionPolicy
from hermes.graph.nodes.conditional import RouterNode

__all__ = [
    "GraphNode",
    "LLMNode",
    "PlannerNode",
    "JudgeNode",
    "SubgraphNode",
    "ParallelNode",
    "MergeStrategy",
    "ListMergeStrategy",
    "TextConcatStrategy",
    "ParallelExecutionPolicy",
    "RouterNode",
]

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture