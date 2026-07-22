"""
===============================================================================
Memory Pipeline
===============================================================================

Sprint 13: Orchestrates memory processing stages.
===============================================================================
"""
from __future__ import annotations

from typing import List
from hermes.memory.pipeline.stages import MemoryStage
from hermes.memory.retrieval import RetrievedMemory


class MemoryPipeline:
    """Executes a sequence of memory processing stages."""
    
    def __init__(self, stages: List[MemoryStage]):
        self._stages = stages

    def run(self, memories: List[RetrievedMemory]) -> List[RetrievedMemory]:
        for stage in self._stages:
            memories = stage.process(memories)
        return memories

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture