"""Rate limiting utilities for FastAPI."""

import time
from collections import defaultdict
from typing import Any, Callable, Dict, Optional

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimiter:
    """Simple in-memory rate limiter.

    For production use, consider Redis-based rate limiting.
    """

    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        requests_per_day: int = 10000,
    ):
        """Initialize rate limiter.

        Args:
            requests_per_minute: Maximum requests per minute
            requests_per_hour: Maximum requests per hour
            requests_per_day: Maximum requests per day
        """
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.requests_per_day = requests_per_day

        # Track requests by identifier (IP, user ID, etc.)
        self.minute_requests: Dict[str, list[float]] = defaultdict(list)
        self.hour_requests: Dict[str, list[float]] = defaultdict(list)
        self.day_requests: Dict[str, list[float]] = defaultdict(list)

    def _cleanup_old_requests(self, requests: list[float], window_seconds: float) -> None:
        """Remove requests outside the time window."""
        current_time = time.time()
        cutoff = current_time - window_seconds
        requests[:] = [req_time for req_time in requests if req_time > cutoff]

    def is_allowed(self, identifier: str) -> tuple[bool, Optional[str]]:
        """Check if request is allowed.

        Args:
            identifier: Request identifier (IP, user ID, etc.)

        Returns:
            Tuple of (is_allowed, error_message)
        """
        current_time = time.time()

        # Check minute limit
        self._cleanup_old_requests(self.minute_requests[identifier], 60)
        if len(self.minute_requests[identifier]) >= self.requests_per_minute:
            return False, "Rate limit exceeded: too many requests per minute"

        # Check hour limit
        self._cleanup_old_requests(self.hour_requests[identifier], 3600)
        if len(self.hour_requests[identifier]) >= self.requests_per_hour:
            return False, "Rate limit exceeded: too many requests per hour"

        # Check day limit
        self._cleanup_old_requests(self.day_requests[identifier], 86400)
        if len(self.day_requests[identifier]) >= self.requests_per_day:
            return False, "Rate limit exceeded: too many requests per day"

        # Record request
        self.minute_requests[identifier].append(current_time)
        self.hour_requests[identifier].append(current_time)
        self.day_requests[identifier].append(current_time)

        return True, None


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting requests."""

    def __init__(
        self,
        app: Any,
        rate_limiter: Optional[RateLimiter] = None,
        identifier_func: Optional[Callable[[Request], str]] = None,
        exclude_paths: Optional[list[str]] = None,
    ):
        """Initialize rate limit middleware.

        Args:
            app: FastAPI application
            rate_limiter: Optional rate limiter instance (creates default if None)
            identifier_func: Function to extract identifier from request (default: IP address)
            exclude_paths: List of paths to exclude from rate limiting
        """
        super().__init__(app)
        self.rate_limiter = rate_limiter or RateLimiter()
        self.identifier_func = identifier_func or self._get_client_ip
        self.exclude_paths = exclude_paths or ["/health", "/metrics"]

    @staticmethod
    def _get_client_ip(request: Request) -> str:
        """Extract client IP from request."""
        if request.client:
            return request.client.host
        return "unknown"

    async def dispatch(self, request: Request, call_next: Callable):
        """Apply rate limiting to request."""
        # Skip rate limiting for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        # Get identifier
        identifier = self.identifier_func(request)

        # Check rate limit
        is_allowed, error_message = self.rate_limiter.is_allowed(identifier)
        if not is_allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=error_message,
                headers={"Retry-After": "60"},
            )

        return await call_next(request)


def create_rate_limit_middleware(
    requests_per_minute: int = 60,
    requests_per_hour: int = 1000,
    requests_per_day: int = 10000,
    exclude_paths: Optional[list[str]] = None,
) -> RateLimitMiddleware:
    """Create a rate limit middleware with default configuration.

    Args:
        requests_per_minute: Maximum requests per minute
        requests_per_hour: Maximum requests per hour
        requests_per_day: Maximum requests per day
        exclude_paths: List of paths to exclude

    Returns:
        RateLimitMiddleware instance
    """
    rate_limiter = RateLimiter(
        requests_per_minute=requests_per_minute,
        requests_per_hour=requests_per_hour,
        requests_per_day=requests_per_day,
    )
    return RateLimitMiddleware(
        app=None,  # Will be set by FastAPI
        rate_limiter=rate_limiter,
        exclude_paths=exclude_paths,
    )
