"""Request/response logging middleware for FastAPI."""

import logging
import time
from typing import Any, Callable, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestResponseLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging request and response details."""

    def __init__(
        self,
        app: Any,
        log_level: int = logging.INFO,
        log_request_body: bool = False,
        log_response_body: bool = False,
        exclude_paths: Optional[list[str]] = None,
    ):
        """Initialize logging middleware.

        Args:
            app: FastAPI application
            log_level: Logging level (default: INFO)
            log_request_body: Whether to log request body
            log_response_body: Whether to log response body
            exclude_paths: List of paths to exclude from logging
        """
        super().__init__(app)
        self.log_level = log_level
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.exclude_paths = exclude_paths or ["/health", "/metrics"]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request and response details."""
        # Skip logging for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        # Extract request details
        request_id = getattr(request.state, "request_id", None)
        method = request.method
        path = request.url.path
        query_params = str(request.query_params) if request.query_params else None

        # Log request
        log_data = {
            "request_id": request_id,
            "method": method,
            "path": path,
            "query_params": query_params,
            "client_host": request.client.host if request.client else None,
        }

        if self.log_request_body:
            try:
                body = await request.body()
                log_data["body"] = body.decode("utf-8")[:500]  # Limit body size
            except Exception:
                log_data["body"] = "<unable to read>"

        logger.log(
            self.log_level,
            f"Request: {method} {path}",
            extra=log_data,
        )

        # Process request
        start_time = time.time()
        try:
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000

            # Log response
            response_log_data = {
                "request_id": request_id,
                "method": method,
                "path": path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            }

            if self.log_response_body:
                # Note: Response body streaming makes this complex
                # For now, we log status and duration
                pass

            logger.log(
                self.log_level,
                f"Response: {method} {path} - {response.status_code} ({duration_ms:.2f}ms)",
                extra=response_log_data,
            )

            return response
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                f"Request error: {method} {path} - {str(e)} ({duration_ms:.2f}ms)",
                extra={"request_id": request_id, "error": str(e)},
                exc_info=True,
            )
            raise
