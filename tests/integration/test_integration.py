"""Integration tests for shared-ai-utils package."""

from unittest.mock import Mock

import pytest
from shared_ai_utils import (
    AssessmentEngine,
    AssessmentInput,
    ConfigBase,
    LLMManager,
    PathType,
    PatternManager,
    PresetManager,
    RequestIDMiddleware,
    create_health_router,
    get_preset,
    print_success,
)


class TestIntegration:
    """Test that all components work together."""

    def test_all_imports(self):
        """Test that all main components can be imported."""
        # This test verifies the package structure is correct
        assert AssessmentEngine is not None
        assert LLMManager is not None
        assert PatternManager is not None
        assert ConfigBase is not None
        assert PresetManager is not None

    def test_config_and_presets(self):
        """Test config and preset integration."""
        preset = get_preset("development")
        assert isinstance(preset, dict)
        assert "APP_ENV" in preset

    def test_cli_utilities(self):
        """Test CLI utilities work."""
        # Should not raise
        print_success("Test message")

    @pytest.mark.asyncio
    async def test_assessment_engine_basic(self):
        """Test assessment engine works."""
        engine = AssessmentEngine()
        input_data = AssessmentInput(
            candidate_id="test",
            submission_type="code",
            content={"code": "def hello(): return 'world'"},
            paths_to_evaluate=[PathType.TECHNICAL],
        )

        result = await engine.assess(input_data)
        assert result.overall_score >= 0.0
        assert result.overall_score <= 100.0

    def test_pattern_manager_basic(self):
        """Test pattern manager works."""
        import tempfile
        from pathlib import Path

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            manager = PatternManager(pattern_library_path=temp_path)
            pattern = manager.add_pattern(
                name="test",
                description="Test pattern",
                good_example="def good(): pass",
            )
            assert pattern["name"] == "test"
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_health_router(self):
        """Test health router creation."""
        router = create_health_router(version="1.0.0")
        assert router is not None

    def test_request_id_middleware(self):
        """Test request ID middleware can be instantiated."""
        middleware = RequestIDMiddleware(Mock())
        assert middleware is not None
