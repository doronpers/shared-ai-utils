"""
FastAPI Utilities

Production-ready middleware, error handling, health check, logging,
rate limiting, authentication, and WebSocket utilities.
"""

from shared_ai_utils.api.auth import (
    create_api_key_auth,
    get_api_key_from_request,
    hash_api_key,
    verify_api_key,
    verify_api_key_dependency,
)
from shared_ai_utils.api.errors import (
    ErrorCode,
    ErrorResponse,
    create_error_response,
    file_upload_error,
    internal_error,
    not_found_error,
    service_unavailable_error,
    validation_error,
)
from shared_ai_utils.api.health import HealthResponse, create_health_router
from shared_ai_utils.api.logging import RequestResponseLoggingMiddleware
from shared_ai_utils.api.middleware import RequestIDMiddleware, create_cors_middleware
from shared_ai_utils.api.rate_limit import (
    RateLimiter,
    RateLimitMiddleware,
    create_rate_limit_middleware,
)
from shared_ai_utils.api.websocket import (
    WebSocketManager,
    websocket_endpoint,
)

__all__ = [
    # Middleware
    "RequestIDMiddleware",
    "RequestResponseLoggingMiddleware",
    "create_cors_middleware",
    # Rate Limiting
    "RateLimiter",
    "RateLimitMiddleware",
    "create_rate_limit_middleware",
    # Authentication
    "verify_api_key",
    "verify_api_key_dependency",
    "create_api_key_auth",
    "get_api_key_from_request",
    "hash_api_key",
    # Error Handling
    "ErrorCode",
    "ErrorResponse",
    "create_error_response",
    "validation_error",
    "not_found_error",
    "internal_error",
    "service_unavailable_error",
    "file_upload_error",
    # Health
    "HealthResponse",
    "create_health_router",
    # WebSocket
    "WebSocketManager",
    "websocket_endpoint",
]
