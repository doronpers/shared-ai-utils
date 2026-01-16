"""
FastAPI Utilities

Production-ready middleware, error handling, and health check utilities.
"""

from .errors import (
    ErrorCode,
    ErrorResponse,
    create_error_response,
    file_upload_error,
    internal_error,
    not_found_error,
    service_unavailable_error,
    validation_error,
)
from .health import HealthResponse, create_health_router
from .middleware import RequestIDMiddleware, create_cors_middleware

__all__ = [
    "RequestIDMiddleware",
    "create_cors_middleware",
    "ErrorCode",
    "ErrorResponse",
    "create_error_response",
    "validation_error",
    "not_found_error",
    "internal_error",
    "service_unavailable_error",
    "file_upload_error",
    "HealthResponse",
    "create_health_router",
]
