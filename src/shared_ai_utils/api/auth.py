"""Authentication helpers for FastAPI."""

import hashlib
import hmac
import logging
from typing import Optional

from fastapi import HTTPException, Request, Security, status
from fastapi.security import APIKeyHeader, HTTPBearer

logger = logging.getLogger(__name__)

# Security schemes
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
bearer_scheme = HTTPBearer(auto_error=False)


def verify_api_key(api_key: str, expected_key: str) -> bool:
    """Verify an API key using constant-time comparison.

    Args:
        api_key: API key to verify
        expected_key: Expected API key

    Returns:
        True if keys match, False otherwise
    """
    if not api_key or not expected_key:
        return False
    return hmac.compare_digest(api_key.encode(), expected_key.encode())


def get_api_key_from_request(request: Request) -> Optional[str]:
    """Extract API key from request headers.

    Args:
        request: FastAPI request

    Returns:
        API key if present, None otherwise
    """
    # Try X-API-Key header
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return api_key

    # Try Authorization header with Bearer token
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:]

    return None


async def verify_api_key_dependency(
    request: Request,
    expected_key: Optional[str] = None,
    api_key_env_var: str = "API_KEY",
) -> str:
    """Dependency for verifying API key in FastAPI routes.

    Args:
        request: FastAPI request
        expected_key: Expected API key (if None, reads from environment)
        api_key_env_var: Environment variable name for API key

    Returns:
        API key if valid

    Raises:
        HTTPException: If API key is invalid or missing
    """
    import os

    if expected_key is None:
        expected_key = os.getenv(api_key_env_var)

    if not expected_key:
        logger.warning("API key verification enabled but no expected key configured")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key verification not configured",
        )

    api_key = get_api_key_from_request(request)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if not verify_api_key(api_key, expected_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    return api_key


def create_api_key_auth(expected_key: Optional[str] = None) -> Callable:
    """Create an API key authentication dependency.

    Args:
        expected_key: Expected API key (if None, reads from API_KEY env var)

    Returns:
        Dependency function for FastAPI routes
    """
    async def auth_dependency(request: Request) -> str:
        return await verify_api_key_dependency(request, expected_key)

    return auth_dependency


def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage (one-way hash).

    Args:
        api_key: API key to hash

    Returns:
        SHA-256 hash of the API key
    """
    return hashlib.sha256(api_key.encode()).hexdigest()
