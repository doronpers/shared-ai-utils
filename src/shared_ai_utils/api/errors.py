"""
Standardized Error Handling

Consistent error response format and error codes for FastAPI applications.
"""

from typing import Any, Dict, Optional

from fastapi import HTTPException, status
from pydantic import BaseModel


class ErrorCode:
    """Standard error codes for API responses."""

    # Validation errors (400)
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    INVALID_FORMAT = "INVALID_FORMAT"

    # Authentication/Authorization errors (401, 403)
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"

    # Not found errors (404)
    NOT_FOUND = "NOT_FOUND"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"

    # Conflict errors (409)
    CONFLICT = "CONFLICT"
    DUPLICATE_RESOURCE = "DUPLICATE_RESOURCE"

    # Server errors (500, 503)
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    DATABASE_ERROR = "DATABASE_ERROR"

    # Rate limiting (429)
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

    # Bad request (400)
    BAD_REQUEST = "BAD_REQUEST"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    INVALID_FILE_TYPE = "INVALID_FILE_TYPE"


class ErrorResponse(BaseModel):
    """Standard error response format."""

    error: bool = True
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None


def create_error_response(
    error_code: str,
    message: str,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
) -> HTTPException:
    """
    Create a standardized HTTP exception with error response.

    Args:
        error_code: Standard error code from ErrorCode
        message: Human-readable error message
        status_code: HTTP status code
        details: Optional additional error details
        request_id: Optional request ID for tracking

    Returns:
        HTTPException with standardized error response
    """
    error_response = ErrorResponse(
        error=True,
        error_code=error_code,
        message=message,
        details=details,
        request_id=request_id,
    )

    return HTTPException(
        status_code=status_code,
        detail=error_response.model_dump(exclude_none=True),
    )


def validation_error(
    message: str,
    field: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
) -> HTTPException:
    """Create a validation error response."""
    error_details = details or {}
    if field:
        error_details["field"] = field

    return create_error_response(
        error_code=ErrorCode.VALIDATION_ERROR,
        message=message,
        status_code=status.HTTP_400_BAD_REQUEST,
        details=error_details,
        request_id=request_id,
    )


def not_found_error(
    resource_type: str,
    resource_id: Optional[str] = None,
    request_id: Optional[str] = None,
) -> HTTPException:
    """Create a not found error response."""
    message = f"{resource_type} not found"
    if resource_id:
        message += f": {resource_id}"

    return create_error_response(
        error_code=ErrorCode.NOT_FOUND,
        message=message,
        status_code=status.HTTP_404_NOT_FOUND,
        details={"resource_type": resource_type, "resource_id": resource_id},
        request_id=request_id,
    )


def internal_error(
    message: str = "An internal error occurred",
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
) -> HTTPException:
    """Create an internal server error response."""
    return create_error_response(
        error_code=ErrorCode.INTERNAL_ERROR,
        message=message,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        details=details,
        request_id=request_id,
    )


def service_unavailable_error(
    service: str,
    request_id: Optional[str] = None,
) -> HTTPException:
    """Create a service unavailable error response."""
    return create_error_response(
        error_code=ErrorCode.SERVICE_UNAVAILABLE,
        message=f"{service} is currently unavailable",
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        details={"service": service},
        request_id=request_id,
    )


def file_upload_error(
    message: str,
    error_type: str = ErrorCode.INVALID_FILE_TYPE,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
) -> HTTPException:
    """Create a file upload error response."""
    return create_error_response(
        error_code=error_type,
        message=message,
        status_code=status.HTTP_400_BAD_REQUEST,
        details=details,
        request_id=request_id,
    )
