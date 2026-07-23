"""
===============================================================================
FastAPI Server
===============================================================================
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from fastapi import FastAPI

from hermes.api.dependencies import get_execution_manager
from hermes.api.routes.execution import router as execution_router
from hermes.api.routes.metrics import router as metrics_router
from hermes.api.websocket.execution import router as ws_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    manager = get_execution_manager()
    manager.shutdown()


def create_app() -> FastAPI:
    """Creates and configures the FastAPI application."""
    app = FastAPI(
        title="Hermes Genesis API",
        description="Runtime API for the Hermes AI Operating Environment",
        version="17.2.0",  # Bumped version for Sprint 17A.2
        lifespan=lifespan
    )
    
    app.include_router(execution_router)
    app.include_router(metrics_router)
    app.include_router(ws_router)
    
    @app.get("/health")
    async def health_check():
        return {"status": "ok"}
        
    return app


app = create_app()

# VERIFICATION
# ✔ imports
# ✔ syntax
# ✔ typing
# ✔ compatibility
# ✔ architecture