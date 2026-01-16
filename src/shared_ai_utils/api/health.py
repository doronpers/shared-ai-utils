"""
Health Check Utilities

Reusable health check endpoints for FastAPI applications.
"""

from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional

from fastapi import APIRouter, Request
from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    timestamp: str
    components: Dict[str, str]
    details: Optional[Dict[str, Any]] = None


def create_health_router(
    version: str = "0.1.0",
    component_checker: Optional[Callable[[], Dict[str, str]]] = None,
    details_checker: Optional[Callable[[], Dict[str, Any]]] = None,
) -> APIRouter:
    """
    Create a health check router.

    Args:
        version: Application version
        component_checker: Optional function that returns component statuses
        details_checker: Optional function that returns detailed component info

    Returns:
        APIRouter with health check endpoints
    """
    router = APIRouter()

    @router.get("/health", response_model=HealthResponse)
    async def health_check(request: Request):
        """Health check endpoint."""
        components = {}
        details = None

        # Use custom checkers if provided
        if component_checker:
            components = component_checker()
        else:
            # Default: all healthy
            components = {"api": "operational"}

        if details_checker:
            details = details_checker()

        # Determine overall status
        status = "healthy"
        if any(v in ["unavailable", "degraded", "error"] for v in components.values()):
            status = "degraded"
        if all(v in ["unavailable", "error"] for v in components.values()):
            status = "unhealthy"

        return HealthResponse(
            status=status,
            version=version,
            timestamp=datetime.now(timezone.utc).isoformat(),
            components=components,
            details=details,
        )

    @router.get("/", response_model=Dict[str, Any])
    async def root():
        """Root endpoint with API information."""
        return {
            "name": "API",
            "version": version,
            "status": "operational",
            "endpoints": {
                "health": "/health",
                "docs": "/docs",
            },
        }

    return router
