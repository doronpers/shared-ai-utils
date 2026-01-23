"""Dashboard configuration templates for analytics visualization.

Provides ready-to-use dashboard configurations for:
- Assessment metrics (sono-eval)
- Sensor metrics (sono-platform)
- Pattern metrics (feedback-loop)
- Unified cross-repo dashboard
"""

from typing import Any, Dict, List


def create_unified_dashboard_config(
    title: str = "Cross-Repository Analytics",
    include_assessment: bool = True,
    include_sensor: bool = True,
    include_pattern: bool = True,
    include_api: bool = True,
) -> Dict[str, Any]:
    """Create a unified dashboard configuration for cross-repo analytics.

    Args:
        title: Dashboard title
        include_assessment: Include assessment metrics
        include_sensor: Include sensor metrics
        include_pattern: Include pattern metrics
        include_api: Include API metrics

    Returns:
        Dashboard configuration dictionary
    """
    charts = []

    # Assessment metrics charts
    if include_assessment:
        charts.extend([
            {
                "type": "line",
                "title": "Assessment Scores Over Time",
                "query": """
                    SELECT 
                        DATE(timestamp) as date,
                        AVG(overall_score) as avg_score,
                        COUNT(*) as assessment_count
                    FROM assessments
                    GROUP BY DATE(timestamp)
                    ORDER BY date DESC
                """,
            },
            {
                "type": "bar",
                "title": "Assessment Scores by Path",
                "query": """
                    SELECT 
                        path,
                        AVG(score) as avg_score,
                        COUNT(*) as count
                    FROM assessment_scores
                    GROUP BY path
                """,
            },
        ])

    # Sensor metrics charts
    if include_sensor:
        charts.extend([
            {
                "type": "line",
                "title": "Sensor Performance Over Time",
                "query": """
                    SELECT 
                        DATE(timestamp) as date,
                        sensor_name,
                        AVG(processing_time_ms) as avg_time
                    FROM sensors
                    GROUP BY DATE(timestamp), sensor_name
                    ORDER BY date DESC
                """,
            },
            {
                "type": "pie",
                "title": "Sensor Verdict Distribution",
                "query": """
                    SELECT 
                        verdict,
                        COUNT(*) as count
                    FROM sensor_verdicts
                    GROUP BY verdict
                """,
            },
        ])

    # Pattern metrics charts
    if include_pattern:
        charts.extend([
            {
                "type": "bar",
                "title": "Pattern Violations by Severity",
                "query": """
                    SELECT 
                        severity,
                        COUNT(*) as count
                    FROM pattern_violations
                    GROUP BY severity
                """,
            },
            {
                "type": "line",
                "title": "Pattern Effectiveness Over Time",
                "query": """
                    SELECT 
                        DATE(timestamp) as date,
                        pattern,
                        AVG(effectiveness_score) as avg_effectiveness
                    FROM patterns
                    GROUP BY DATE(timestamp), pattern
                    ORDER BY date DESC
                """,
            },
        ])

    # API metrics charts
    if include_api:
        charts.extend([
            {
                "type": "line",
                "title": "API Request Rate",
                "query": """
                    SELECT 
                        DATE(timestamp) as date,
                        COUNT(*) as request_count,
                        AVG(response_time_ms) as avg_response_time
                    FROM api_requests
                    GROUP BY DATE(timestamp)
                    ORDER BY date DESC
                """,
            },
            {
                "type": "bar",
                "title": "API Errors by Status Code",
                "query": """
                    SELECT 
                        status_code,
                        COUNT(*) as error_count
                    FROM api_errors
                    GROUP BY status_code
                """,
            },
        ])

    return {
        "title": title,
        "charts": charts,
        "metadata": {
            "version": "1.0",
            "created_at": "2026-01-21",
            "includes": {
                "assessment": include_assessment,
                "sensor": include_sensor,
                "pattern": include_pattern,
                "api": include_api,
            },
        },
    }


def create_assessment_dashboard_config(title: str = "Assessment Analytics") -> Dict[str, Any]:
    """Create dashboard configuration for assessment metrics.

    Args:
        title: Dashboard title

    Returns:
        Dashboard configuration dictionary
    """
    return {
        "title": title,
        "charts": [
            {
                "type": "line",
                "title": "Overall Scores Over Time",
                "query": """
                    SELECT 
                        DATE(timestamp) as date,
                        AVG(overall_score) as avg_score,
                        MIN(overall_score) as min_score,
                        MAX(overall_score) as max_score
                    FROM assessments
                    GROUP BY DATE(timestamp)
                    ORDER BY date DESC
                """,
            },
            {
                "type": "bar",
                "title": "Scores by Assessment Path",
                "query": """
                    SELECT 
                        path,
                        AVG(score) as avg_score,
                        COUNT(*) as count
                    FROM assessment_scores
                    GROUP BY path
                    ORDER BY avg_score DESC
                """,
            },
            {
                "type": "table",
                "title": "Recent Assessments",
                "query": """
                    SELECT 
                        candidate_id,
                        overall_score,
                        confidence,
                        processing_time_ms,
                        timestamp
                    FROM assessments
                    ORDER BY timestamp DESC
                    LIMIT 50
                """,
            },
            {
                "type": "pie",
                "title": "Dominant Path Distribution",
                "query": """
                    SELECT 
                        dominant_path,
                        COUNT(*) as count
                    FROM assessments
                    WHERE dominant_path IS NOT NULL
                    GROUP BY dominant_path
                """,
            },
        ],
    }


def create_sensor_dashboard_config(title: str = "Sensor Performance Analytics") -> Dict[str, Any]:
    """Create dashboard configuration for sensor metrics.

    Args:
        title: Dashboard title

    Returns:
        Dashboard configuration dictionary
    """
    return {
        "title": title,
        "charts": [
            {
                "type": "line",
                "title": "Sensor Processing Time",
                "query": """
                    SELECT 
                        DATE(timestamp) as date,
                        sensor_name,
                        AVG(processing_time_ms) as avg_time,
                        P95(processing_time_ms) as p95_time
                    FROM sensors
                    GROUP BY DATE(timestamp), sensor_name
                    ORDER BY date DESC
                """,
            },
            {
                "type": "bar",
                "title": "Sensor Verdict Distribution",
                "query": """
                    SELECT 
                        sensor_name,
                        verdict,
                        COUNT(*) as count
                    FROM sensor_verdicts
                    GROUP BY sensor_name, verdict
                """,
            },
            {
                "type": "table",
                "title": "Sensor Performance Summary",
                "query": """
                    SELECT 
                        sensor_name,
                        COUNT(*) as total_analyses,
                        AVG(processing_time_ms) as avg_time,
                        SUM(CASE WHEN passed = true THEN 1 ELSE 0 END) as pass_count,
                        SUM(CASE WHEN passed = false THEN 1 ELSE 0 END) as fail_count
                    FROM sensors
                    GROUP BY sensor_name
                """,
            },
        ],
    }


def create_pattern_dashboard_config(title: str = "Pattern Analysis Dashboard") -> Dict[str, Any]:
    """Create dashboard configuration for pattern metrics.

    Args:
        title: Dashboard title

    Returns:
        Dashboard configuration dictionary
    """
    return {
        "title": title,
        "charts": [
            {
                "type": "bar",
                "title": "Pattern Violations by Pattern",
                "query": """
                    SELECT 
                        pattern,
                        COUNT(*) as violation_count
                    FROM pattern_violations
                    GROUP BY pattern
                    ORDER BY violation_count DESC
                """,
            },
            {
                "type": "bar",
                "title": "Violations by Severity",
                "query": """
                    SELECT 
                        severity,
                        COUNT(*) as count
                    FROM pattern_violations
                    GROUP BY severity
                    ORDER BY 
                        CASE severity
                            WHEN 'critical' THEN 1
                            WHEN 'high' THEN 2
                            WHEN 'medium' THEN 3
                            WHEN 'low' THEN 4
                        END
                """,
            },
            {
                "type": "line",
                "title": "Pattern Effectiveness Trends",
                "query": """
                    SELECT 
                        DATE(timestamp) as date,
                        pattern,
                        AVG(effectiveness_score) as avg_effectiveness
                    FROM patterns
                    GROUP BY DATE(timestamp), pattern
                    ORDER BY date DESC
                """,
            },
            {
                "type": "table",
                "title": "Top Patterns by Effectiveness",
                "query": """
                    SELECT 
                        pattern,
                        AVG(effectiveness_score) as avg_effectiveness,
                        SUM(success_count) as total_successes,
                        SUM(failure_count) as total_failures
                    FROM patterns
                    GROUP BY pattern
                    ORDER BY avg_effectiveness DESC
                    LIMIT 20
                """,
            },
        ],
    }


def export_dashboard_to_superset(
    dashboard_config: Dict[str, Any],
    output_file: str = "dashboard.json",
) -> None:
    """Export dashboard configuration to Superset-compatible JSON.

    Args:
        dashboard_config: Dashboard configuration dictionary
        output_file: Output file path
    """
    import json

    with open(output_file, "w") as f:
        json.dump(dashboard_config, f, indent=2)
