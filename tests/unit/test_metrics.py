"""Tests for metrics collector."""

import pytest
from datetime import datetime

from shared_ai_utils.metrics import MetricsCollector, MetricType


class TestMetricsCollector:
    """Test MetricsCollector."""

    @pytest.fixture
    def collector(self):
        """Create metrics collector instance."""
        return MetricsCollector()

    def test_collector_initialization(self, collector):
        """Test collector initialization."""
        assert collector.data is not None
        assert len(collector.data) > 0
        assert "assessments" in collector.data

    def test_get_metric_categories(self, collector):
        """Test getting metric categories."""
        categories = MetricsCollector.get_metric_categories()
        assert isinstance(categories, list)
        assert len(categories) > 0
        assert "assessments" in categories

    def test_log_assessment(self, collector):
        """Test logging assessment metrics."""
        collector.log_assessment(
            candidate_id="test_candidate",
            assessment_id="assess_123",
            overall_score=85.5,
            path_scores=[{"path": "technical", "score": 90.0}],
            processing_time_ms=150.0,
        )

        assert len(collector.data["assessments"]) == 1
        entry = collector.data["assessments"][0]
        assert entry["candidate_id"] == "test_candidate"
        assert entry["overall_score"] == 85.5

    def test_log_api_request(self, collector):
        """Test logging API request metrics."""
        collector.log_api_request(
            method="POST",
            path="/api/test",
            status_code=200,
            response_time_ms=50.0,
        )

        assert len(collector.data["api_requests"]) == 1
        entry = collector.data["api_requests"][0]
        assert entry["path"] == "/api/test"
        assert entry["status_code"] == 200

    def test_log_error(self, collector):
        """Test logging error metrics."""
        collector.log_error(
            error_type="ValueError",
            error_message="Test error",
        )

        assert len(collector.data["errors"]) == 1
        entry = collector.data["errors"][0]
        assert entry["error_type"] == "ValueError"
        assert entry["error_message"] == "Test error"

    def test_log_llm_call(self, collector):
        """Test logging LLM call metrics."""
        collector.log_llm_call(
            provider="anthropic",
            model="claude-sonnet-4",
            success=True,
            duration_ms=500.0,
            token_count=300,
        )

        assert len(collector.data["llm_calls"]) == 1
        entry = collector.data["llm_calls"][0]
        assert entry["provider"] == "anthropic"
        assert entry["token_count"] == 300

    def test_multiple_metric_types(self, collector):
        """Test logging multiple metric types."""
        collector.log_assessment(
            candidate_id="test",
            assessment_id="assess_1",
            overall_score=80.0,
            path_scores=[],
            processing_time_ms=100.0,
        )
        collector.log_api_request(
            method="GET",
            path="/api/test",
            status_code=200,
            response_time_ms=50.0,
        )

        assert len(collector.data["assessments"]) == 1
        assert len(collector.data["api_requests"]) == 1
        assert collector.data["assessments"][0]["overall_score"] == 80.0
        assert collector.data["api_requests"][0]["path"] == "/api/test"

    def test_clear_metrics(self, collector):
        """Test clearing metrics."""
        collector.log_assessment(
            candidate_id="test",
            assessment_id="assess_1",
            overall_score=80.0,
            path_scores=[],
            processing_time_ms=100.0,
        )

        assert len(collector.data["assessments"]) == 1
        # Clear by resetting data
        for category in collector.data:
            collector.data[category].clear()
        assert len(collector.data["assessments"]) == 0
