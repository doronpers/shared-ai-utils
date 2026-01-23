"""Unified metrics collector supporting all metric types across repositories.

Supports:
- Assessment metrics (sono-eval)
- Sensor metrics (sono-platform)
- Pattern metrics (feedback-loop)
- API metrics (all repos)
- Performance metrics
- Error tracking
"""

import json
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Types of metrics supported by the unified framework."""

    # Assessment metrics
    ASSESSMENT = "assessment"
    ASSESSMENT_SCORE = "assessment_score"
    ASSESSMENT_PATH = "assessment_path"

    # Sensor metrics (sono-platform)
    SENSOR = "sensor"
    SENSOR_VERDICT = "sensor_verdict"
    SENSOR_PERFORMANCE = "sensor_performance"

    # Pattern metrics (feedback-loop)
    PATTERN = "pattern"
    PATTERN_VIOLATION = "pattern_violation"
    PATTERN_EFFECTIVENESS = "pattern_effectiveness"

    # API metrics
    API_REQUEST = "api_request"
    API_RESPONSE = "api_response"
    API_ERROR = "api_error"

    # Performance metrics
    PERFORMANCE = "performance"
    MEMORY_USAGE = "memory_usage"
    EXECUTION_TIME = "execution_time"

    # Error tracking
    ERROR = "error"
    BUG = "bug"
    TEST_FAILURE = "test_failure"

    # LLM metrics
    LLM_CALL = "llm_call"
    LLM_TOKEN_USAGE = "llm_token_usage"

    # Code generation
    CODE_GENERATION = "code_generation"

    # Deployment
    DEPLOYMENT = "deployment"
    DEPLOYMENT_ISSUE = "deployment_issue"


class MetricsCollector:
    """Unified metrics collector supporting all metric types across repositories."""

    # Extended metric categories for cross-repo support
    METRIC_CATEGORIES = [
        # Assessment
        "assessments",
        "assessment_scores",
        # Sensor
        "sensors",
        "sensor_verdicts",
        # Pattern
        "patterns",
        "pattern_violations",
        # API
        "api_requests",
        "api_responses",
        "api_errors",
        # Performance
        "performance_metrics",
        "memory_usage",
        "execution_times",
        # Errors
        "errors",
        "bugs",
        "test_failures",
        # LLM
        "llm_calls",
        "llm_token_usage",
        # Code generation
        "code_generation",
        # Deployment
        "deployments",
        "deployment_issues",
    ]

    def __init__(self, memory_service: Optional[Any] = None):
        """Initialize the metrics collector.

        Args:
            memory_service: Optional memory service for persistence (e.g., MemU)
        """
        self.data: Dict[str, List[Dict[str, Any]]] = {
            category: [] for category in self.METRIC_CATEGORIES
        }
        self.memory_service = memory_service

    @classmethod
    def get_metric_categories(cls) -> List[str]:
        """Get the list of metric categories.

        Returns:
            List of metric category names
        """
        return cls.METRIC_CATEGORIES.copy()

    # Assessment metrics

    def log_assessment(
        self,
        candidate_id: str,
        assessment_id: str,
        overall_score: float,
        path_scores: List[Dict[str, Any]],
        processing_time_ms: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log an assessment event.

        Args:
            candidate_id: Candidate identifier
            assessment_id: Assessment identifier
            overall_score: Overall assessment score
            path_scores: List of path score dictionaries
            processing_time_ms: Processing time in milliseconds
            metadata: Optional additional metadata
        """
        entry = {
            "candidate_id": candidate_id,
            "assessment_id": assessment_id,
            "overall_score": overall_score,
            "path_scores": path_scores,
            "processing_time_ms": processing_time_ms,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
        }
        self.data["assessments"].append(entry)
        logger.debug(f"Logged assessment: {assessment_id}")

    def log_assessment_score(
        self,
        assessment_id: str,
        path: str,
        score: float,
        confidence: float,
        metrics: List[Dict[str, Any]],
    ) -> None:
        """Log an assessment path score.

        Args:
            assessment_id: Assessment identifier
            path: Assessment path (technical, design, etc.)
            score: Path score
            confidence: Confidence level
            metrics: List of scoring metrics
        """
        entry = {
            "assessment_id": assessment_id,
            "path": path,
            "score": score,
            "confidence": confidence,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat(),
        }
        self.data["assessment_scores"].append(entry)

    # Sensor metrics

    def log_sensor(
        self,
        sensor_name: str,
        verdict: str,
        value: float,
        threshold: float,
        processing_time_ms: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log a sensor analysis event.

        Args:
            sensor_name: Name of the sensor
            verdict: Verdict (pass/fail/info)
            value: Sensor value
            threshold: Threshold used
            processing_time_ms: Processing time in milliseconds
            metadata: Optional additional metadata
        """
        entry = {
            "sensor_name": sensor_name,
            "verdict": verdict,
            "value": value,
            "threshold": threshold,
            "processing_time_ms": processing_time_ms,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
        }
        self.data["sensors"].append(entry)
        logger.debug(f"Logged sensor: {sensor_name}")

    def log_sensor_verdict(
        self,
        sensor_name: str,
        passed: Optional[bool],
        confidence: float,
        evidence: List[Dict[str, Any]],
    ) -> None:
        """Log a sensor verdict.

        Args:
            sensor_name: Name of the sensor
            passed: Whether sensor passed (None for info-only)
            confidence: Confidence level
            evidence: List of evidence dictionaries
        """
        entry = {
            "sensor_name": sensor_name,
            "passed": passed,
            "confidence": confidence,
            "evidence": evidence,
            "timestamp": datetime.now().isoformat(),
        }
        self.data["sensor_verdicts"].append(entry)

    # Pattern metrics

    def log_pattern_violation(
        self,
        pattern: str,
        line: int,
        code: str,
        description: str,
        severity: str,
        file_path: str,
    ) -> None:
        """Log a pattern violation.

        Args:
            pattern: Pattern name
            line: Line number
            code: Code snippet
            description: Violation description
            severity: Severity level (low/medium/high/critical)
            file_path: File path
        """
        entry = {
            "pattern": pattern,
            "line": line,
            "code": code,
            "description": description,
            "severity": severity,
            "file_path": file_path,
            "timestamp": datetime.now().isoformat(),
        }
        self.data["pattern_violations"].append(entry)
        logger.debug(f"Logged pattern violation: {pattern}")

    def log_pattern_effectiveness(
        self,
        pattern: str,
        success_count: int,
        failure_count: int,
        effectiveness_score: float,
    ) -> None:
        """Log pattern effectiveness metrics.

        Args:
            pattern: Pattern name
            success_count: Number of successful applications
            failure_count: Number of failures
            effectiveness_score: Effectiveness score (0-1)
        """
        entry = {
            "pattern": pattern,
            "success_count": success_count,
            "failure_count": failure_count,
            "effectiveness_score": effectiveness_score,
            "timestamp": datetime.now().isoformat(),
        }
        self.data["patterns"].append(entry)

    # API metrics

    def log_api_request(
        self,
        method: str,
        path: str,
        status_code: int,
        response_time_ms: float,
        request_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log an API request.

        Args:
            method: HTTP method
            path: Request path
            status_code: HTTP status code
            response_time_ms: Response time in milliseconds
            request_id: Optional request ID
            metadata: Optional additional metadata
        """
        entry = {
            "method": method,
            "path": path,
            "status_code": status_code,
            "response_time_ms": response_time_ms,
            "request_id": request_id,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
        }
        self.data["api_requests"].append(entry)

    def log_api_error(
        self,
        method: str,
        path: str,
        status_code: int,
        error_message: str,
        request_id: Optional[str] = None,
    ) -> None:
        """Log an API error.

        Args:
            method: HTTP method
            path: Request path
            status_code: HTTP status code
            error_message: Error message
            request_id: Optional request ID
        """
        entry = {
            "method": method,
            "path": path,
            "status_code": status_code,
            "error_message": error_message,
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
        }
        self.data["api_errors"].append(entry)
        logger.debug(f"Logged API error: {path} - {status_code}")

    # Performance metrics

    def log_performance_metric(
        self,
        metric_type: str,
        value: float,
        unit: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log a performance metric.

        Args:
            metric_type: Type of metric (e.g., "memory_usage", "execution_time")
            value: Metric value
            unit: Unit of measurement
            metadata: Optional additional metadata
        """
        entry = {
            "metric_type": metric_type,
            "value": value,
            "unit": unit,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
        }
        self.data["performance_metrics"].append(entry)

    def log_execution_time(
        self,
        operation: str,
        duration_ms: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log execution time for an operation.

        Args:
            operation: Operation name
            duration_ms: Duration in milliseconds
            metadata: Optional additional metadata
        """
        self.log_performance_metric(
            metric_type="execution_time",
            value=duration_ms,
            unit="ms",
            metadata={"operation": operation, **(metadata or {})},
        )

    # Error tracking

    def log_error(
        self,
        error_type: str,
        error_message: str,
        file_path: Optional[str] = None,
        line: Optional[int] = None,
        stack_trace: Optional[str] = None,
    ) -> None:
        """Log an error.

        Args:
            error_type: Type of error
            error_message: Error message
            file_path: Optional file path
            line: Optional line number
            stack_trace: Optional stack trace
        """
        entry = {
            "error_type": error_type,
            "error_message": error_message,
            "file_path": file_path,
            "line": line,
            "stack_trace": stack_trace,
            "timestamp": datetime.now().isoformat(),
        }
        self.data["errors"].append(entry)
        logger.debug(f"Logged error: {error_type}")

    def log_bug(
        self,
        pattern: str,
        error: str,
        code: str,
        file_path: str,
        line: int,
        stack_trace: Optional[str] = None,
    ) -> None:
        """Log a bug occurrence.

        Args:
            pattern: Pattern type
            error: Error message
            code: Code snippet
            file_path: File path
            line: Line number
            stack_trace: Optional stack trace
        """
        entry = {
            "pattern": pattern,
            "error": error,
            "code": code,
            "file_path": file_path,
            "line": line,
            "stack_trace": stack_trace,
            "timestamp": datetime.now().isoformat(),
            "count": 1,
        }
        self.data["bugs"].append(entry)
        logger.debug(f"Logged bug: {pattern}")

    def log_test_failure(
        self,
        test_name: str,
        failure_reason: str,
        pattern_violated: Optional[str] = None,
        code_snippet: Optional[str] = None,
    ) -> None:
        """Log a test failure.

        Args:
            test_name: Test name
            failure_reason: Reason for failure
            pattern_violated: Optional pattern that was violated
            code_snippet: Optional code snippet
        """
        entry = {
            "test_name": test_name,
            "failure_reason": failure_reason,
            "pattern_violated": pattern_violated,
            "code_snippet": code_snippet,
            "timestamp": datetime.now().isoformat(),
        }
        self.data["test_failures"].append(entry)
        logger.debug(f"Logged test failure: {test_name}")

    # LLM metrics

    def log_llm_call(
        self,
        provider: str,
        model: str,
        success: bool,
        duration_ms: float,
        token_count: Optional[int] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log an LLM call.

        Args:
            provider: LLM provider name
            model: Model name
            success: Whether call was successful
            duration_ms: Duration in milliseconds
            token_count: Optional token count
            error: Optional error message
            metadata: Optional additional metadata
        """
        entry = {
            "provider": provider,
            "model": model,
            "success": success,
            "duration_ms": duration_ms,
            "token_count": token_count,
            "error": error,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
        }
        self.data["llm_calls"].append(entry)
        logger.debug(f"Logged LLM call: {provider}/{model}")

    # Code generation

    def log_code_generation(
        self,
        prompt: str,
        patterns_applied: List[str],
        success: bool,
        code_length: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log a code generation event.

        Args:
            prompt: The prompt used
            patterns_applied: List of pattern names applied
            success: Whether generation was successful
            code_length: Optional length of generated code
            metadata: Optional additional metadata
        """
        entry = {
            "prompt": prompt[:200],  # Limit prompt length
            "patterns_applied": patterns_applied,
            "success": success,
            "code_length": code_length,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
        }
        self.data["code_generation"].append(entry)
        logger.debug(f"Logged code generation: {len(patterns_applied)} patterns")

    # Utility methods

    def export_json(self) -> str:
        """Export all collected metrics as JSON.

        Returns:
            JSON string of all metrics
        """
        return json.dumps(self.data, indent=2)

    def export_dict(self) -> Dict[str, List[Dict[str, Any]]]:
        """Export all collected metrics as dictionary.

        Returns:
            Dictionary of all metrics
        """
        return self.data.copy()

    def get_summary(self) -> Dict[str, int]:
        """Get a summary count of all metrics.

        Returns:
            Dictionary with counts of each metric type
        """
        summary = {category: len(self.data[category]) for category in self.METRIC_CATEGORIES}
        summary["total"] = sum(len(v) for v in self.data.values())
        return summary

    def clear(self) -> None:
        """Clear all collected metrics."""
        self.data = {category: [] for category in self.METRIC_CATEGORIES}
        logger.debug("Cleared all metrics")

    def get_metrics_by_type(self, metric_type: MetricType) -> List[Dict[str, Any]]:
        """Get metrics of a specific type.

        Args:
            metric_type: Type of metric to retrieve

        Returns:
            List of metric entries
        """
        category_map = {
            MetricType.ASSESSMENT: "assessments",
            MetricType.ASSESSMENT_SCORE: "assessment_scores",
            MetricType.SENSOR: "sensors",
            MetricType.SENSOR_VERDICT: "sensor_verdicts",
            MetricType.PATTERN_VIOLATION: "pattern_violations",
            MetricType.API_REQUEST: "api_requests",
            MetricType.API_ERROR: "api_errors",
            MetricType.PERFORMANCE: "performance_metrics",
            MetricType.ERROR: "errors",
            MetricType.BUG: "bugs",
            MetricType.TEST_FAILURE: "test_failures",
            MetricType.LLM_CALL: "llm_calls",
            MetricType.CODE_GENERATION: "code_generation",
        }
        category = category_map.get(metric_type)
        if category:
            return self.data.get(category, [])
        return []


def get_metric_categories() -> List[str]:
    """Get the list of metric categories.

    Returns:
        List of metric category names
    """
    return MetricsCollector.get_metric_categories()
