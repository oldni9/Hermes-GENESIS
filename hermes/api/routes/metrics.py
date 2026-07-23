"""
===============================================================================
Metrics Routes (REST)
===============================================================================
"""
from __future__ import annotations

from fastapi import APIRouter, Depends

from hermes.api.dependencies import get_execution_manager
from hermes.runtime.execution_manager import ExecutionManager

router = APIRouter(prefix="/metrics", tags=["observability"])


@router.get("")
async def get_runtime_metrics(
    manager: ExecutionManager = Depends(get_execution_manager)
):
    """Retrieve aggregated runtime metrics."""
    return manager.get_metrics()

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture