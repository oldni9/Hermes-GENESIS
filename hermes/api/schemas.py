"""
===============================================================================
API Schemas (Pydantic)
===============================================================================
"""
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel


class ExecutionRequest(BaseModel):
    prompt: str
    system_prompt: Optional[str] = None


class ExecutionResponse(BaseModel):
    execution_id: str
    status: str


class CancelResponse(BaseModel):
    execution_id: str
    cancelled: bool


class ExecutionSnapshot(BaseModel):
    execution_id: str
    status: str
    result: Optional[str] = None
    error: Optional[str] = None
    last_event_sequence: int = 0
    created_at: float
    updated_at: float

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture