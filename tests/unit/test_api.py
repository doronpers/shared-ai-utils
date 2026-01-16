"""Tests for FastAPI utilities."""

import uuid
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from shared_ai_utils.api.errors import (
    ErrorCode,
    ErrorResponse,
    create_error_response,
    internal_error,
    not_found_error,
    validation_error,
)
from shared_ai_utils.api.health import HealthResponse, create_health_router
from shared_ai_utils.api.middleware import RequestIDMiddleware, create_cors_middleware


class TestErrorCode:
    """Test ErrorCode enum."""

    def test_error_codes_exist(self):
        """Test that error codes are defined."""
        assert ErrorCode.VALIDATION_ERROR
        assert ErrorCode.NOT_FOUND
        assert ErrorCode.INTERNAL_ERROR
        assert ErrorCode.SERVICE_UNAVAILABLE


class TestErrorResponse:
    """Test ErrorResponse model."""

    def test_error_response_creation(self):
        """Test creating error response."""
        response = ErrorResponse(
            error_code=ErrorCode.VALIDATION_ERROR,
            message="Test error",
        )
        assert response.error is True
        assert response.error_code == ErrorCode.VALIDATION_ERROR
        assert response.message == "Test error"

    def test_error_response_with_details(self):
        """Test error response with details."""
        response = ErrorResponse(
            error_code=ErrorCode.VALIDATION_ERROR,
            message="Test error",
            details={"field": "email"},
            request_id="test-id",
        )
        assert response.details == {"field": "email"}
        assert response.request_id == "test-id"


class TestErrorFunctions:
    """Test error creation functions."""

    def test_validation_error(self):
        """Test validation error creation."""
        error = validation_error("Invalid input", field="email")
        assert error.status_code == 400
        detail = error.detail
        assert detail["error_code"] == ErrorCode.VALIDATION_ERROR
        assert detail["message"] == "Invalid input"
        assert detail["details"]["field"] == "email"

    def test_not_found_error(self):
        """Test not found error creation."""
        error = not_found_error("User", resource_id="123")
        assert error.status_code == 404
        detail = error.detail
        assert detail["error_code"] == ErrorCode.NOT_FOUND
        assert "User" in detail["message"]

    def test_internal_error(self):
        """Test internal error creation."""
        error = internal_error("Something went wrong")
        assert error.status_code == 500
        detail = error.detail
        assert detail["error_code"] == ErrorCode.INTERNAL_ERROR


class TestRequestIDMiddleware:
    """Test RequestIDMiddleware."""

    @pytest.mark.asyncio
    async def test_middleware_adds_request_id(self):
        """Test that middleware adds request ID."""
        middleware = RequestIDMiddleware(Mock())

        request = Mock(spec=Request)
        request.headers = {}
        request.state = Mock()
        request.method = "GET"
        request.url.path = "/test"

        call_next = AsyncMock(return_value=Mock(headers={}))

        response = await middleware.dispatch(request, call_next)

        assert hasattr(request.state, "request_id")
        assert "X-Request-ID" in response.headers

    @pytest.mark.asyncio
    async def test_middleware_uses_existing_request_id(self):
        """Test that middleware uses existing request ID."""
        middleware = RequestIDMiddleware(Mock())

        request = Mock(spec=Request)
        existing_id = str(uuid.uuid4())
        request.headers = {"X-Request-ID": existing_id}
        request.state = Mock()
        request.method = "GET"
        request.url.path = "/test"

        call_next = AsyncMock(return_value=Mock(headers={}))

        response = await middleware.dispatch(request, call_next)

        assert request.state.request_id == existing_id
        assert response.headers["X-Request-ID"] == existing_id


class TestCORSMiddleware:
    """Test CORS middleware creation."""

    def test_create_cors_middleware_development(self):
        """Test creating CORS middleware for development."""
        config = create_cors_middleware(app_env="development")
        assert config is not None
        assert "allow_origins" in config
        assert "*" in config["allow_origins"]

    def test_create_cors_middleware_production_fails_without_origins(self):
        """Test that production CORS requires explicit origins."""
        with pytest.raises(ValueError, match="ALLOWED_ORIGINS"):
            create_cors_middleware(app_env="production", allowed_origins=None)

    def test_create_cors_middleware_production_with_origins(self):
        """Test creating CORS middleware for production with origins."""
        config = create_cors_middleware(
            app_env="production", allowed_origins=["https://example.com"]
        )
        assert config is not None
        assert "https://example.com" in config["allow_origins"]


class TestHealthRouter:
    """Test health check router."""

    def test_health_router_creation(self):
        """Test creating health router."""
        router = create_health_router(version="1.0.0")
        assert router is not None

    def test_health_endpoint(self):
        """Test health check endpoint."""
        router = create_health_router(version="1.0.0")
        app = FastAPI()
        app.include_router(router)

        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "degraded", "unhealthy"]
        assert data["version"] == "1.0.0"
        assert "timestamp" in data
        assert "components" in data

    def test_root_endpoint(self):
        """Test root endpoint."""
        router = create_health_router(version="1.0.0")
        app = FastAPI()
        app.include_router(router)

        client = TestClient(app)
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "1.0.0"
        assert "endpoints" in data
