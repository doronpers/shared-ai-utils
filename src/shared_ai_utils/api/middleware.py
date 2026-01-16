"""
FastAPI Middleware

Request ID tracking and CORS configuration.
"""

import logging
import uuid
from time import time
from typing import Any, Dict, List, Optional

from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add unique request ID to each request."""

    async def dispatch(self, request: Request, call_next):
        """Add request ID and log request details."""
        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Add to request state
        request.state.request_id = request_id

        # Log request start
        start_time = time()
        logger.debug(
            f"Request started: {request.method} {request.url.path}",
            extra={"request_id": request_id},
        )

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time() - start_time) * 1000

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            # Log request completion
            logger.debug(
                f"Request completed: {request.method} {request.url.path} - Status: {response.status_code}",
                extra={"request_id": request_id, "duration_ms": duration_ms},
            )

            return response
        except Exception as e:
            # Log error with request ID
            duration_ms = (time() - start_time) * 1000
            logger.error(
                f"Request failed: {request.method} {request.url.path} - Error: {str(e)}",
                extra={"request_id": request_id, "duration_ms": duration_ms},
                exc_info=True,
            )
            raise


def create_cors_middleware(
    allowed_origins: Optional[List[str]] = None,
    app_env: str = "development",
    allow_credentials: bool = True,
    allow_methods: Optional[List[str]] = None,
    allow_headers: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Create CORS middleware with production validation.

    Args:
        allowed_origins: List of allowed origins (None = auto-detect from app_env)
        app_env: Application environment ("production" or "development")
        allow_credentials: Allow credentials in CORS requests
        allow_methods: Allowed HTTP methods (default: GET, POST, PUT, DELETE, OPTIONS)
        allow_headers: Allowed headers (default: ["*"])

    Returns:
        CORSMiddleware instance

    Raises:
        ValueError: If production environment has insecure CORS configuration
    """
    if allowed_origins is None:
        if app_env == "production":
            # Production: require explicit origins
            raise ValueError(
                "ALLOWED_ORIGINS must be configured in production. Set specific domains."
            )
        else:
            # Development: allow all origins but log warning
            allowed_origins = ["*"]
            logger.warning("Development mode: CORS origins = ['*']")

    if app_env == "production":
        if not allowed_origins or "*" in allowed_origins:
            logger.error("CRITICAL: ALLOWED_ORIGINS must be configured in production. Set specific domains.")
            raise ValueError("ALLOWED_ORIGINS must be set to specific origins in production environment")
        logger.info(f"Production CORS configured for origins: {allowed_origins}")
    else:
        logger.debug(f"Development mode: CORS origins = {allowed_origins}")

    # Return configuration dict that can be used to create CORSMiddleware
    return {
        "allow_origins": allowed_origins,
        "allow_credentials": allow_credentials,
        "allow_methods": allow_methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": allow_headers or ["*"],
    }
